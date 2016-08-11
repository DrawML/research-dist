import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.DEALER)
socket.bind("tcp://*:7777")

socket.send_multipart([b'aa', b'what?', b'', b'hello', b'', b'final'])
print(socket.recv())
print(socket.recv())
print(socket.recv())
print(socket.recv())

"""
#time.sleep(10)
print("bye1")
router.send(b"bye1")
time.sleep(15)
"""