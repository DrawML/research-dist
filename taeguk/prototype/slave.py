#!/usr/bin/python3
#-*- coding: utf-8 -*-

import zmq
import time
import threading

context = zmq.Context()
socket = context.socket(zmq.DEALER)
socket.connect("tcp://localhost:5560")

def worker(workload):
    print("get work. ({})".format(workload))
    time.sleep(10)
    socket.send(b"finish____" + workload)
    print("send result.")

socket.send(b"ready_____")
print("send ready")
while True:
    msg = socket.recv()
    header = msg[0:10]
    body = msg[10:]

    if header == b"heartbeat_":
        print("heartbeat!")
        socket.send(msg)
    elif header == b"workload__":
        worker_thread = threading.Thread(target=worker, args=(body))
        worker_thread.start()