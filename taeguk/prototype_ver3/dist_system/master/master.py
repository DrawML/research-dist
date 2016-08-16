import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio
from .msg_handler import ClientMessageHandler, SlaveMessageHandler
from .controller import run_heartbeat


class ClientRouter(object):

    def __init__(self, context, addr, msg_handler):
        self._context = context
        self._addr = addr
        self._msg_handler = msg_handler

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            msg = await self._router.recv_multipart()
            await self._process(msg)

    async def _process(self, msg):
        # separate msg into header and body using protocol.*
        header, body = ("dummy", "dummy")

        # handle message
        self._msg_handler.handle_msg(header, msg)



class SlaveRouter(object):
    def __init__(self, context, addr, msg_handler):
        self._context = context
        self._addr = addr
        self._msg_handler = msg_handler

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            msg = await self._router.recv_multipart()
            await self._process(msg)

    async def _process(self, msg):
        # separate msg into header and body using protocol.*
        header, body = ("dummy", "dummy")

        # handle message
        self._msg_handler.handle_msg(header, msg)


async def run_master(context : Context, client_router_addr : str, slave_router_addr : str):

    client_router = ClientRouter(context, client_router_addr, ClientMessageHandler())
    slave_router = SlaveRouter(context, slave_router_addr, SlaveMessageHandler())

    asyncio.wait([
        asyncio.ensure_future(client_router.run()),
        asyncio.ensure_future(slave_router.run()),
        asyncio.ensure_future(run_heartbeat())
    ])


def main(client_router_addr, slave_router_addr):
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)

        context = Context()

        loop.run_until_complete(run_master(context, client_router_addr, slave_router_addr))
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)