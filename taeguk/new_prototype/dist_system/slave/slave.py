#!/usr/bin/python3
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .worker import *
from .task import *

class MasterConnection(object):

    def __init__(self, context, master_addr):
        self._context = context
        self._master_addr = master_addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.connect(self._master_addr)

        while True:
            await self._ready()
            msg = await self._router.recv_multipart()
            await self._process(msg)

    async def ready(self):
        self.dispatch_msg(b"Register")

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        #assert self._master_addr == addr

        if header == b"TaskRequest":
            worker = Worker()
            id = int.from_bytes(body[0:4])
            job = SleepTaskJob.from_bytes(body[4:8])
            task = SleepTask(job, id)
            worker.start(WORKER_ROUTER_ADDR, task)
        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        addr = msg[0]
        assert msg[1] == b""
        header = msg[2]
        assert msg[3] == b""
        body = msg[4]

        return addr, header, body

    def dispatch_msg(self, header, body = b""):

        async def _dispatch_msg(self, msg):
            await self._router.send_multipart(msg)

        msg = [self._master_addr, b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class WorkerRouter(object):

    def __init__(self, context, addr):
        self._context = context
        self._addr = addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            msg = await self._router.recv_multipart()
            await self._process(msg)

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        if header == b"Ready":
            pass
        elif header == b"TaskFinish":
            pass
        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        addr = msg[0]
        assert msg[1] == b""
        header = msg[2]
        assert msg[3] == b""
        body = msg[4]

        return addr, header, body

    def dispatch_msg(self, addr, header, body):

        async def _dispatch_msg(self, msg):
            await self._router.send_multipart(msg)

        msg = [addr, b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


MASTER_ADDR = 'tcp://127.0.0.1:6000'
WORKER_ROUTER_ADDR = 'rpc://'

context = Context()
master_conn = MasterConnection(context, MASTER_ADDR)
worker_router = WorkerRouter(context, WORKER_ROUTER_ADDR)
worker_manager = WorkerManager()

async def run_server():
    asyncio.ensure_future(master_conn.run())
    await worker_router.run()


def main():
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)


if __name__ == '__main__':
    main()