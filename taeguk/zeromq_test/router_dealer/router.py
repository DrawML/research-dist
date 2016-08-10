import zmq
import time

context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:7777")

#time.sleep(10)
print("bye1")
router.send(b"bye1")
time.sleep(15)
