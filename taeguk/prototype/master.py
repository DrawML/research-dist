#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Assumption :
1. Master never die.

"""

"""
Disconnection process will be added....
"""

import zmq

# Prepare our context and sockets
context = zmq.Context()
sock_client = context.socket(zmq.ROUTER)
sock_worker = context.socket(zmq.ROUTER)
sock_client.bind("tcp://*:5559")
sock_worker.bind("tcp://*:5560")

# Initialize poll set
poller = zmq.Poller()
poller.register(sock_client, zmq.POLLIN)
poller.register(sock_worker, zmq.POLLIN)

class Client(object):
    def __init__(self, addr):
        self._addr = addr

    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Task(object):
    def __init__(self, data, client):
        self._data = data
        self._client = client
        self._no = None

    @property
    def priority(self):
        return 1

    @property
    def no(self):
        return self._no

    @no.setter
    def no(self, no):
        self._no = no

    @property
    def client(self):
        return self._client

    @property
    def data(self):
        return self._data


class Worker(object):
    def __init__(self, addr):
        self._addr = addr
        self._no = None
        self._doing_task = None

    def __eq__(self, other):
        return self._addr == other._addr

    def do_task(self, task):
        sock_worker.send_multipart([self.addr, b'', task.data])
        self.doing_task = task

    @property
    def no(self):
        return self._no

    @no.setter
    def no(self, no):
        self._no = no

    @property
    def addr(self):
        return self._addr

    @property
    def doing_task(self):
        return self._doing_task

    @doing_task.setter
    def doing_task(self, task):
        self._doing_task = task


class WorkerManager(object):
    def __init__(self):
        self._workers = []

    def add_worker(self, worker):
        if self.check_worker_existence(worker):
            # error.
            raise ValueError("Duplicated Worker.")
        else:
            worker.no = self.count()
            self._workers.append(worker)

    def del_worker(self, worker):
        if self.check_worker_existence(worker):
            self._workers.remove(worker)
        else:
            # error.
            raise ValueError("Non-existent Worker.")

    def check_worker_existence(self, worker):
        return worker in self._workers

    def count(self):
        return len(self._workers)

    # Get available worker for processing task.
    def get_worker(self, task):
        # some algorithms will be filled in here.
        available_workers = [w for w in self._workers if w.doing_task is None]
        if not available_workers:
            raise Exception("Not available Workers.")
        import random
        worker = random.choice(available_workers)
        return worker

    def find_worker(self, worker):
        if self.check_worker_existence(worker):
            return self._workers[self._workers.index(worker)]
        else:
            # error.
            raise ValueError("Non-existent Worker.")

class TaskQueue(object):
    def __init__(self):
        self._tasks = []

    def count(self):
        return len(self._tasks)

    def push(self, task):
        self._tasks.append(task)
        print("[*] Task Queue Size =", self.count())

    # will be optimized.
    def top(self):
        sel_task = None
        sel_priority = -1
        for task in self._tasks:
            priority = task.priority
            if priority > sel_priority:
                sel_priority = priority
                sel_task = task

        if sel_task is None:
            raise ValueError("No tasks in task queue.")

        return sel_task

    # will be optimized.
    def pop(self):
        sel_task = None
        sel_priority = -1
        for task in self._tasks:
            priority = task.priority
            if priority > sel_priority:
                sel_priority = priority
                sel_task = task

        if sel_task is None:
            raise ValueError("No tasks in task queue.")

        self._tasks.remove(sel_task)

    def process(self):
        try:
            task = self.top()

            try:
                worker = worker_manager.get_worker(task)
                self.pop()
                worker.do_task(task)
                print("[*] Task Queue Size =", self.count())
            except Exception as err:
                print("[!]", err)

        except ValueError as err:
            print("[!]", err)

task_queue = TaskQueue()
worker_manager = WorkerManager()

def communicate_with_client():
    address, empty, message = sock_client.recv_multipart()
    client = Client(address)
    task = Task(message, client)
    task_queue.push(task)
    task_queue.process()

def communicate_with_worker():
    address, empty, message = sock_worker.recv_multipart()

    worker = Worker(address)

    # will be modified.
    header = message[0:10]
    body = message[10:]

    if header == b'ready_____':
        try:
            worker_manager.add_worker(worker)
            print("[*] Worker {0} is ready!".format(worker.no))
            task_queue.process()
        except ValueError as err:
            print("[!]", err)

    elif header == b'finish____':
        real_worker = worker_manager.find_worker(worker)
        print("[*] Worker {0} is finished!".format(real_worker.no))
        task = real_worker.doing_task
        client = task.client
        sock_client.send_multipart([client.addr, b'', body])
        real_worker.doing_task = None
        task_queue.process()

    elif header == b'exit______':
        raise NotImplementedError()

    else:
        raise ValueError("Unknown Message.")

# Switch messages between sockets
while True:
    print("loop!")
    socks = dict(poller.poll())

    if socks.get(sock_client) == zmq.POLLIN:
        print("[*] sock_client pollin!")
        communicate_with_client()

    if socks.get(sock_worker) == zmq.POLLIN:
        print("[*] sock_worker pollin!")
        communicate_with_worker()