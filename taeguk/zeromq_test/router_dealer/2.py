import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://127.0.0.1:7777")


print(socket.recv())
print(socket.recv())
print(socket.recv())
#socket.send_multipart([b'', b'hello'])
socket.send(b'asdf')
"""

msg = socket.recv_multipart()
addr, other = msg
print(msg)
socket.send_multipart([addr, b'hello'])
"""
"""
time.sleep(3)
print("hello1")
dealer.send(b"hello1")
print("hello2")
dealer.send(b"hello2")
print("hello3")
dealer.send(b"hello3")
"""