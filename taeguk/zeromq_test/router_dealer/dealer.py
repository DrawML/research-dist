import zmq
import time

context = zmq.Context()
dealer = context.socket(zmq.DEALER)
dealer.connect("tcp://localhost:7777")

time.sleep(10)
print("hello1")
dealer.send(b"hello1")
print("hello2")
dealer.send(b"hello2")
print("hello3")
dealer.send(b"hello3")