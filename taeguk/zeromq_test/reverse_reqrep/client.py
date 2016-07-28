#!/usr/bin/python3
#-*- coding: utf-8 -*-

import zmq
import time

context = zmq.Context()

print("Connecting to hello world server…")
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5555")

while True:
    message = socket.recv()
    print("Received request: %s" % message)

    time.sleep(10)

    socket.send(b"World")