#!/usr/bin/python3
#-*- coding: utf-8 -*-

import zmq
import time

NUM_CLIENTS = 10

def simulate(id):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")

    for req in range(10):
        print("[{}] Send request {}-{}".format(id, id, req))
        socket.send("Hello({}-{})".format(id, req).encode('utf-8'))
        message = socket.recv()
        print("[{}] Received reply : {}".format(id , message))
        time.sleep(3)

if __name__ == '__main__':
    # spawn workers
    from multiprocessing import Process
    for i in range(NUM_CLIENTS):
        Process(target=simulate, args=(i,)).start()
        time.sleep(1)