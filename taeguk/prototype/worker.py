#!/usr/bin/python3
#-*- coding: utf-8 -*-

import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5560")

socket.send(b"ready_____")
print("send ready")
while True:
    workload = socket.recv()
    print("get work.")
    time.sleep(2)
    socket.send(b"finish____" + workload)
    print("send result.")