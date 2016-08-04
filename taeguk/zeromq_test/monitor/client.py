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

line = lambda: print('-' * 40)


ctx = zmq.Context.instance()
rep = ctx.socket(zmq.REP)

line()
print("connect rep")
rep.connect("tcp://127.0.0.1:6666")
time.sleep(10)

line()
print("disconnect rep")
rep.disconnect("tcp://127.0.0.1:6666")
time.sleep(1)

line()
print("close rep")
rep.close()

print("END")
ctx.term()