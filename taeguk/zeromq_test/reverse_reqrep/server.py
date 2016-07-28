#!/usr/bin/python3
#-*- coding: utf-8 -*-

import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.bind("tcp://*:5555")

for request in range(10):
    print("Sending request %s …" % request)
    socket.send(b"Hello")

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))