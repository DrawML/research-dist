# -*- coding: utf-8 -*-
"""Simple example demonstrating the use of the socket monitoring feature."""

# This file is part of pyzmq.
#
# Distributed under the terms of the New BSD License. The full
# license is in the file COPYING.BSD, distributed as part of this
# software.
from __future__ import print_function

__author__ = 'Guido Goldstein'

import threading
import time

import zmq
from zmq.utils.monitor import recv_monitor_message


line = lambda: print('-' * 40)


print("libzmq-%s" % zmq.zmq_version())
if zmq.zmq_version_info() < (4, 0):
    raise RuntimeError("monitoring in libzmq version < 4.0 is not supported")

EVENT_MAP = {}
print("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        print("%21s : %4i" % (name, value))
        EVENT_MAP[value] = name


def event_monitor(monitor):
    while monitor.poll():
        evt = recv_monitor_message(monitor)
        evt.update({'description': EVENT_MAP[evt['event']]})
        print("Event: {}".format(evt))
        if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
            break
    monitor.close()
    print()
    print("event monitor thread done!")


ctx = zmq.Context.instance()
req = ctx.socket(zmq.REQ)

monitor = req.get_monitor_socket()

t = threading.Thread(target=event_monitor, args=(monitor,))
t.start()

line()
print("bind req")
req.bind("tcp://127.0.0.1:6666")

time.sleep(10)

line()
print("disabling event monitor")
req.disable_monitor()

line()
print("event monitor thread should now terminate")

line()
print("close req")
req.close()

print("END")
ctx.term()