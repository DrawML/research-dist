#!/usr/bin/python3
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .worker import *

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

        if header == b"TaskStart":

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
WORKER_ROUTER_ADDR = 'tcp://127.0.0.1:5556'

context = Context()
master_conn = MasterConnection()

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


if __name__ == '__main__':
    main()