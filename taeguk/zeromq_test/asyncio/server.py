#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio


Url = 'tcp://127.0.0.1:5555'
Ctx = Context()


async def run():
    print("Getting ready for hello world client.  Ctrl-C to exit.\n")
    socket = Ctx.socket(zmq.REP)
    socket.bind(Url)
    while True:
        #  Wait for next request from client
        message = await socket.recv()
        print("Received request: {}".format(message))
        #  Do some "work"
        await asyncio.sleep(1)
        #  Send reply back to client
        message = message.decode('utf-8')
        message = '{}, world'.format(message)
        message = message.encode('utf-8')
        print("Sending reply: {}".format(message))
        await socket.send(message)


def main():
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)


if __name__ == '__main__':
    main()