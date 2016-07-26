import zmq
import time

context = zmq.Context()

client_url = "tcp://*:5555"
worker_url = "tcp://*:5556"

client_router = context.socket(zmq.ROUTER)
client_router.bind(client_url)

worker_router = context.socket(zmq.ROUTER)
worker_router.bind(worker_url)

poller = zmq.Poller()
poller.register(client_router, zmq.POLLIN)
poller.register(worker_router, zmq.POLLIN)

client_n = 0
worker_queue = []
client_queue = []

def logger(tag, action, msg):
    print("[%s/%s] %s" % (tag, action, msg))

while True:
    # logger("master", "POLLING", "waiting...")
    socks = dict(poller.poll())

    if worker_router in socks and socks[worker_router] == zmq.POLLIN:
        msg = worker_router.recv_multipart()

        worker_addr = msg[0]

        if len(client_queue) > 0:
            (client_addr, request) = client_queue.pop()
            worker_router.send_multipart([worker_addr, b"", client_addr, b"", request])
        else:
            worker_queue.append(worker_addr)

        assert msg[1] == b""
        client_addr = msg[2]

        if client_addr != b"READY":
            assert msg[3] == b""
            reply = msg[4]

            client_router.send_multipart([client_addr, b"", reply])
            client_n -= 1
            logger("master", "ROUTING", "Worker#{0} -> Client#{1}".format(worker_addr, client_addr))
        else:
            logger("master", "QUEUEING", "Worker#{0} is ready.".format(worker_addr)) # improve

    if client_router in socks and socks[client_router] == zmq.POLLIN:
        [client_addr, empty, request] = client_router.recv_multipart()

        assert empty == b""

        if len(worker_queue) > 0:
            worker_addr = worker_queue.pop()
            worker_router.send_multipart([worker_addr, b"", client_addr, b"", request])
            logger("master", "ROUTING", "Client#{0} -> Worker#{1}".format(client_addr, worker_addr))
        else:
            client_queue.append((client_addr, request)) # problem: have to keep data
            logger("master", "QUEUEING", "Client#{0} is enqueued.".format(client_addr))

time.sleep(1)

client_router.close()
worker_router.close()
context.term()
