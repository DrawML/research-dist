import zmq
import threading
import time
from random import randrange

def worker_thread(_url, context, i):
    master = context.socket(zmq.REQ)
    master.identity = ("Worker-%d" % i).encode('ascii')
    master.connect(_url)

    # [performance, status]
    master.send_multipart([i.to_bytes(1, 'little'), b"", b'READY'])
    print("[%s] I'm ready..." % (master.identity.decode('ascii')))

    while True:
        [client_addr, empty, request] = master.recv_multipart()
        assert empty == b""

        print("[%s] Processing task... %s / %s" % (master.identity.decode('ascii'),
                                                    client_addr.decode('ascii'),
                                                    request.decode('ascii')))

        time.sleep(randrange(1, 10))

        print("[%s] finish task... %s / %s" % (master.identity.decode('ascii'),
                                                    client_addr.decode('ascii'),
                                                    request.decode('ascii')))

        master.send_multipart([i.to_bytes(1, 'little'), b"", client_addr, b"", b"FINISH"])

context = zmq.Context()
master_url = "tcp://localhost:5556"

for i in range(10):
    work_thread = threading.Thread(target=worker_thread, args=(master_url, context, i))
    work_thread.start()
