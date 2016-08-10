#!/usr/bin/python3
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .task import *
from random import randint

class MasterConnection(object):

    def __init__(self, context, master_addr):
        self._context = context
        self._master_addr = master_addr

    async def run(self):
        self._router = self._context.socket(zmq.DEALER)        # if router, sending msg is not working.
        self._router.connect(self._master_addr)
        self._register()    # this must be modified.

        asyncio.ensure_future(task_simulator.run())

        while len(task_manager.complete_tasks) < TaskSimulator.NUM_TASKS:
            print("[Master Connection] before recv.")
            msg = await self._router.recv_multipart()
            print("[Master Connection] after recv.")
            self._process(msg)

    def _register(self):
        self.dispatch_msg(b"Register")

    def _process(self, msg):
        header, body = self._resolve_msg(msg)

        if header == b"TaskAccept":
            print("[Master Connection] TaskAccept packet in.")
            id = int.from_bytes(body[0:4], byteorder='big')
            task_identity = TaskIdentity(id)
            task_manager.change_task_status(task_identity, Task.STATUS_WAITING)

        elif header == b"TaskStart":
            print("[Master Connection] TaskStart packet in.")
            id = int.from_bytes(body[0:4], byteorder='big')
            task_identity = TaskIdentity(id)
            task_manager.change_task_status(task_identity, Task.STATUS_PROCESSING)

        elif header == b"TaskFinish":
            print("[Master Connection] TaskFinish packet in.")
            id = int.from_bytes(body[0:4], byteorder='big')
            task_identity = TaskIdentity(id)
            task = task_manager.find_task(task_identity)
            task.set_result_from_bytes(body[4:])
            task_manager.change_task_status(task_identity, Task.STATUS_COMPLETE)

            print("[*] Task Finish. id = {0}, comment = {1}".format(task.id.id, task.result.comment))

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


class TaskSimulator:

    NUM_TASKS = 1
    SLEEP_TASK_MIN_SECONDS = 1
    SLEEP_TASK_MAX_SECONDS = 10
    TASK_GAP_MIN_SECONDS = 10
    TASK_GAP_MAX_SECONDS = 20

    def __init__(self):
        pass

    def _make_task(self):
        job = SleepTaskJob(randint(TaskSimulator.SLEEP_TASK_MIN_SECONDS, TaskSimulator.SLEEP_TASK_MAX_SECONDS))
        task = SleepTask(job)
        return task

    def _process_task(self, task : SleepTask):
        request_body = task.to_bytes()
        request_body += task.job.to_bytes()
        master_conn.dispatch_msg(b"SleepTask", request_body)

    async def run(self):

        for idx in range(TaskSimulator.NUM_TASKS):
            print("[*] Simulate Task #{0}".format(idx))
            task = self._make_task()
            task_manager.add_task(task)
            self._process_task(task)
            await asyncio.sleep(randint(TaskSimulator.TASK_GAP_MIN_SECONDS, TaskSimulator.TASK_GAP_MAX_SECONDS))


MASTER_ADDR = 'tcp://127.0.0.1:5000'

context = Context()
master_conn = MasterConnection(context, MASTER_ADDR)
task_manager = TaskManager()
task_simulator = TaskSimulator()

async def run_server():
    await master_conn.run()

def main():
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)