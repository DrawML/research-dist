import zmq
import time

class Client:
    def __init__(self, addr):
       self.id = addr 

class Task:
    def __init__(self, job, client):
        self.job = job
        self.client = client;

class Worker:
    def __init__(self, addr, level):
        self.id = addr
        self.level = level

class WorkerQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, worker):
        self.queue.append(worker)
        self.__sort()

    def dequeue(self):
        return self.queue.pop()

    def __sort(self):
        from operator import attrgetter
        self.queue.sort(key=attrgetter('level'), reverse=True)

    def __len__(self):
        return len(self.queue)

class TaskQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, task):
        self.queue.append(task)

    def dequeue(self):
        return self.queue.pop()

    def __len__(self):
        return len(self.queue)


def resolve_worker_msg(msg):
    worker_addr = msg[0]
    assert msg[1] == b""
    worker_level = msg[2]
    assert msg[3] == b""
    client_addr = msg[4] if msg[4] != b"READY" else None
    reply = None

    if client_addr:
        assert msg[5] == b""
        reply = msg[6]

    return (worker_addr, worker_level, client_addr, reply)

def resolve_client_msg(msg):
    client_addr, empty, request = msg
    assert empty == b""

    return (client_addr, request)


def make_msg(*content):
    msg = []
    for c in content:
        msg.append(c)
        msg.append(b'')
    msg.pop()
    return msg 


def send_worker(addr, *content):
    msg = make_msg(addr, *content)
    worker_router.send_multipart(msg)

def reply_client(addr, reply):
    msg = make_msg(addr, reply)
    client_router.send_multipart(msg)


def request_work():
    if len(task_queue) > 0 and len(worker_queue) > 0:
        task = task_queue.dequeue()
        worker = worker_queue.dequeue()
        send_worker(worker.id, task.client.id, task.job)
        logger("master", "ROUTING", "{0} -> {1}".format(task.client.id, worker.id))

    elif len(task_queue) == 0:
        logger("master", "QUEUEING", "Worker is enqueued.")
    elif len(worker_queue) == 0:
        logger("master", "QUEUEING", "Task is enqueued.")

def handle_worker(msg):
    # expected msg schema
    worker_addr, worker_level, client_addr, reply = resolve_worker_msg(msg)

    worker = Worker(worker_addr, worker_level)
    worker_queue.enqueue(worker)

    if client_addr:
        reply_client(client_addr, reply)
        logger("master", "ROUTING", "{0} -> {1}".format(worker.id, client_addr))
    else:
        logger("master", "QUEUEING", "{0} is ready.".format(worker.id)) # improve

def handle_client(msg):
    # expected msg schema
    client_addr, request = resolve_client_msg(msg)

    task = Task(request, Client(client_addr))
    task_queue.enqueue(task)


def logger(tag, action, msg):
    print("[%s/%s] %s" % (tag, action, msg))


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

worker_queue = WorkerQueue() 
task_queue = TaskQueue() 

while True:
    # logger("master", "POLLING", "waiting...")
    socks = dict(poller.poll())

    if socks.get(worker_router) == zmq.POLLIN:
        msg = worker_router.recv_multipart()
        handle_worker(msg)

    if socks.get(client_router) == zmq.POLLIN:
        msg = client_router.recv_multipart()
        handle_client(msg)

    request_work()


time.sleep(1)

client_router.close()
worker_router.close()
context.term()

