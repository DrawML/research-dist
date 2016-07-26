import zmq
import threading


def client_thread(_url, context, i):
    master = context.socket(zmq.REQ)
    master.identity = ("Client-%d" % (i)).encode('ascii')
    master.connect(_url)

    master.send(b"Your task")
    reply = master.recv()
    print("Reply : %s / %s" % (master.identity.decode('ascii'),
                                reply.decode('ascii')))

master_url = "tcp://localhost:5555"
context = zmq.Context()

for i in range(15):
    cli_thread = threading.Thread(target=client_thread, args=(master_url, context, i))
    cli_thread.start()
