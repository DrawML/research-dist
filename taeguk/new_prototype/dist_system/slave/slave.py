#!/usr/bin/python3
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .worker import *
from .task import *
#from concurrent.futures import ProcessPoolExecutor

class MasterConnection(object):

    def __init__(self, context, master_addr):
        self._context = context
        self._master_addr = master_addr

    async def run(self):
        self._router = self._context.socket(zmq.DEALER)        # if router, sending msg is not working.
        self._router.connect(self._master_addr)
        self._register()

        while True:
            print("[Master Connection] before recv.")
            msg = await self._router.recv_multipart()
            print("[Master Connection] after recv.")
            self._process(msg)

    def _register(self):
        self.dispatch_msg(b"Register")

    def _process(self, msg):
        header, body = self._resolve_msg(msg)

        if header == b"SleepTask":

            print("[Master Connection] SleepTask packet in.")
            worker = Worker()
            id = int.from_bytes(body[0:4], byteorder='big')
            job = SleepTaskJob.from_bytes(body[4:8])
            task = SleepTask(job, id)
            worker.start(SLAVE_ADDR, task)
        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        print(msg)
        #addr = msg[0]
        #assert msg[1] == b''
        header = msg[0]
        assert msg[1] == b''
        body = msg[2]

        return header, body

    def dispatch_msg(self, header, body = b''):

        async def _dispatch_msg(msg):
            print("_dispatch_msg("+str(msg)+")")
            await self._router.send_multipart(msg)  # why server cannot receive this msg???
            print("_dispatch_msg finish")   # come here : okay

        msg = [header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class WorkerRouter(object):

    def __init__(self, context, addr):
        self._context = context
        self._addr = addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            print("[Worker Router] before recv.")
            msg = await self._router.recv_multipart()
            print("[Worker Router] after recv.")
            self._process(msg)

    def _process(self, msg):
        addr, identity, header, body = self._resolve_msg(msg)

        identity = identity.decode(encoding='utf-8')
        worker = worker_manager.find_worker(identity)

        if header == b"TaskStart":
            print("[Worker Router] TaskStart packet in.")
            worker.status = Worker.STATUS_WORKING

        elif header == b"TaskFinish":
            print("[Worker Router] TaskFinish packet in.")
            task = worker.task
            task.set_result_from_bytes(body)
            worker.status = Worker.STATUS_FINISHED
            worker_manager.del_worker(worker)

            master_conn.dispatch_msg(b"TaskFinish", task.result.to_bytes())
            self.dispatch_msg(addr, b"Goodbye")

        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        print(msg)
        addr = msg[0]
        assert msg[1] == b''
        identity = msg[2]
        assert msg[3] == b''
        header = msg[4]
        assert msg[5] == b''
        body = msg[6]

        return addr, identity, header, body

    def dispatch_msg(self, addr, header, body = b''):

        async def _dispatch_msg(msg):
            await self._router.send_multipart(msg)

        msg = [addr, b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))

print("!!!!!!!!!!!!!")

MASTER_ADDR = 'tcp://127.0.0.1:6000'
WORKER_ROUTER_ADDR = 'tcp://*:7000'
SLAVE_ADDR = 'tcp://127.0.0.1:7000'
CONTROL_ROUTER_ADDR = 'tcp://*:3000'

async def run_server():
    asyncio.ensure_future(master_conn.run())
    asyncio.ensure_future(worker_router.run())

    # terminate server if receive a control packet from control socket.
    control_router = context.socket(zmq.ROUTER)
    control_router.bind(CONTROL_ROUTER_ADDR)
    msg = await control_router.recv_multipart()

def main():

    global context
    global master_conn
    global worker_router
    global worker_manager

    context = Context()
    master_conn = MasterConnection(context, MASTER_ADDR)
    worker_router = WorkerRouter(context, WORKER_ROUTER_ADDR)
    worker_manager = WorkerManager()


    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        #loop.set_default_executor(ProcessPoolExecutor())
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)