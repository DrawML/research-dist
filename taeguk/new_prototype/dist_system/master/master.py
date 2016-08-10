#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .task import *
from .client import *
from .slave import *

"""
현재 진행도
기본적인 master의 구현완료. 그러나 아직 테스트가 안됨. 버그가 많을 것임.
"""

"""
앞으로 해야할 것.
- 현재 master의 테스트 및 버그 수정.
- connection management 추가 (heartbeat, ...)
- resource monitoring 기능 추가
- protobuf를 이용한 프로토콜 구조화
- exception class 설계 및 detail한 exception 처리.
- 모듈별로 분할. (여러개 파일로 분할)
"""

"""
나중에 다시 생각해 볼 것들)

1. client도 task를, task도 client를 가지고 있는 구조에 대한 고찰.
(task만 client를 가지고 있는 식으로 변경하는 게 옳을 것 같음.)
(slave와 task에 대해서도 같은 이슈가 존재.)
task만 client, slave를 가지고 있는 쪽이 훨씬 더 구조상 안정적이고 버그발생가능성이 낮을 것 같다.

2. Network관련 부분을 따로 독립하는게 낫지 않나?? 그렇다면 어떻게??

3. 의존성 문제에 대한 고려.
의존성 관계가 어떻게 되는지 분석하고 문제가 있으면 고친다.

"""


class ClientRouter(object):

    def __init__(self, context, addr):
        self._context = context
        self._addr = addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            print("[Client Router] before recv.")
            msg = await self._router.recv_multipart()
            print("[Client Router] after recv.")
            await self._process(msg)

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        client_identity = ClientIdentity(addr)

        if header == b"Register":
            print("[Client Router] Register packet in.")
            client_manager.add_client(client_identity)

        elif header == b"SleepTask":
            print("[Client Router] SleepTask packet in.")
            client = client_manager.find_client(client_identity)

            req_id = int.from_bytes(body[0:4], byteorder='big')
            job = SleepTaskJob.from_bytes(body[4:8])
            task = SleepTask(job, client, req_id)

            reply_body = task.req_id.to_bytes()
            self.dispatch_msg(client.addr, b"TaskAccept", reply_body)

            client.have_task(task)
            task_manager.add_task(task)
            scheduler.invoke()

        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        print(msg)
        addr = msg[0]
        #assert msg[1] == b''
        header = msg[1]
        assert msg[2] == b''
        body = msg[3]

        return addr, header, body

    def dispatch_msg(self, addr, header, body = b''):

        async def _dispatch_msg(msg):
            await self._router.send_multipart(msg)

        msg = [addr, header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class SlaveRouter(object):
    def __init__(self, context, addr):
        self._context = context
        self._addr = addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            print("[Slave Router] before recv.")
            msg = await self._router.recv_multipart()
            print("[Slave Router] after recv.")
            await self._process(msg)

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        slave_identity = SlaveIdentity(addr)

        if header == b"Register":
            print("[Slave Router] Register packet in.")
            slave_manager.add_slave(slave_identity)
            scheduler.invoke()

        elif header == b"TaskFinish":
            print("[Slave Router] TaskFinish packet in.")
            task_id = int.from_bytes(body[0:4], byteorder='big')

            task_identity = TaskIdentity(task_id)
            task = task_manager.find_task(task_identity)
            task.set_result_from_bytes(body[4:])

            slave = slave_manager.find_slave(slave_identity)
            slave.delete_task(task_identity)

            task_manager.change_task_status(task_identity, Task.STATUS_COMPLETE)
            scheduler.invoke()

        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        print(msg)
        addr = msg[0]
        #assert msg[1] == b''
        header = msg[1]
        assert msg[2] == b''
        body = msg[3]

        return addr, header, body

    def dispatch_msg(self, addr, header, body = b''):

        async def _dispatch_msg(msg):
            await self._router.send_multipart(msg)

        msg = [addr, header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class Scheduler(object):

    def __init__(self):
        pass

    def invoke(self):
        # 1. 현재 waiting하고 있는 task가 있는 지 보고 available한 slave 있는지 판단하여 task를 slave에 배치한다.
        # 2. 다 처리된 task가 있으면 client에 보고 한다.
        self._assign_waiting_task_to_slave()
        self._report_complete_task_to_client()

    def _assign_waiting_task_to_slave(self):
        for task in task_manager.waiting_tasks:
            client = task.client

            try:
                slave = slave_manager.get_proper_slave(task)
            except Exception as err:
                print("[!]", err)
                continue

            slave.assign_task(task)
            task_manager.change_task_status(task, Task.STATUS_PROCESSING)

            reply_body = task.req_id.to_bytes()
            client_router.dispatch_msg(client.addr, b"TaskStart", reply_body)

            if isinstance(task, SleepTask):
                request_header = b"SleepTask"
            else:
                raise ValueError("Invalid Task Type.")
            request_body = task.to_bytes()
            request_body += task.job.to_bytes()
            slave_router.dispatch_msg(slave.addr, request_header, request_body)


    def _report_complete_task_to_client(self):
        for task in task_manager.complete_tasks:
            client = task.client
            client.lose_task(task)
            task_manager.del_task(task)

            reply_body = task.req_id.to_bytes()
            reply_body += task.result.to_bytes()
            client_router.dispatch_msg(client.addr, b"TaskFinish", reply_body)


CLIENT_ROUTER_ADDR = 'tcp://*:5000'
SLAVE_ROUTER_ADDR = 'tcp://*:6000'
CONTROL_ROUTER_ADDR = 'tcp://*:10000'

context = Context()
client_router = ClientRouter(context, CLIENT_ROUTER_ADDR)
slave_router = SlaveRouter(context, SLAVE_ROUTER_ADDR)

client_manager = ClientManager()
task_manager = TaskManager()
slave_manager = SlaveManager()
scheduler = Scheduler()

async def run_server():
    asyncio.ensure_future(client_router.run())
    asyncio.ensure_future(slave_router.run())

    # terminate server if receive a control packet from control socket.
    control_router = context.socket(zmq.ROUTER)
    control_router.bind(CONTROL_ROUTER_ADDR)
    msg = await control_router.recv_multipart()


def main():
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)