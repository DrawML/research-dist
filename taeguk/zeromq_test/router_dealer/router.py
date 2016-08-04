import zmq
import time

context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:7777")

print("bye1")
router.send(b"bye1")
print("bye2")
router.send(b"bye2")
print("bye3")
router.send(b"bye3")
