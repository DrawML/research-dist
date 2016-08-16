import zmq
import threading

import master_slave_pb2 as protocol

context = zmq.Context()

def replier(_url, context, i):

    while True:
        pass

rep_url = 'tcp://localhost:8885'

rep_sock = context.socket(zmq.REP)
rep_sock.connect(rep_url)

while True:
    data = rep_sock.recv()

    recv_msg = protocol.Message()
    recv_msg.ParseFromString(data)

    print("I'm replier - ", recv_msg)
    data = rep_sock.send_string('OK')
