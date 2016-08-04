import zmq

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
req = ctx.socket(zmq.REQ)

router = ctx.socket(zmq.ROUTER)

router.bind('tcp://*:8888')
pub.connect('tcp://localhost:8888')
req.connect('tcp://localhost:8888')

pub.send(b'publish')
print("publish!")
req.send(b'request')
print("request!")