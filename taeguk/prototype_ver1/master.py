#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Assumption :
1. Master never die.

"""

"""
Disconnection process will be added....

TODO:
1. connection management of Client.
2. `` of Slave.

master : 분산 시스템의 두목
slave : task를 할당받는 자
client : task를 던지는 자.

근데 어차피 셋 다 전부 내부 시스템이 될 것임.
굳히 다양하게 연결불능까지 처리해야할까??

시나리오)
1. slave와 통신이 잘 안 될 때,
    slave의 상테를 통신불능으로 표시해 task가 할당되지 못하게 한다.
2. task를 할당받은 slave와 통신이 잘 안 될 떼,
    특정 timeout만큼 통신되길 기다렸다가, 그래도 실패하면, task를 다시 task queue에 넣고,
    slave에게 표시를 해둔다.
3. 일정 시간 이상 slave와 통신불능일 떼,
    slave와 통신이 영구적으로 끊켰다고 보고, slave와의 연결을 해제하고 관련 처리를 한다.

4. client와 통신이 잘 안 될때, 일정시간 이상 client와 통신 불능일 때,
    slave와 비슷한 방식으로 처리.
5. client에게 task result를 response해야하는데, 통신불능일 떼,
    일단 임시로 '미전달 result 목록'에 넣어놓고 추후에 통신이 가능해졌을 떼 전달해준다.
"""

import zmq
from enum import Enum

class Client(object):
    def __init__(self, addr):
        self._addr = addr

    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class ClientManager(object):
    def __init__(self):
        self._clients = []

    def add_client(self, client):
        pass


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


class TaskManager(object):
    def __init__(self):
        self._tasks = []

    def add_task(self):
        pass


class Slave(object):
    def __init__(self, addr):
        self._addr = addr
        self._no = None
        self._doing_task = None

    def __eq__(self, other):
        return self._addr == other._addr

    def do_task(self, task):
        slave_router.send_multipart([self.addr, b'', task.data])
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


class SlaveManager(object):
    def __init__(self):
        self._slaves = []

    def add_slave(self, slave):
        if self.check_slave_existence(slave):
            # error.
            raise ValueError("Duplicated Slave.")
        else:
            slave.no = self.count()
            self._slaves.append(slave)

    def del_slave(self, slave):
        if self.check_slave_existence(slave):
            self._slaves.remove(slave)
        else:
            # error.
            raise ValueError("Non-existent Slave.")

    def check_slave_existence(self, slave):
        return slave in self._slaves

    def count(self):
        return len(self._slaves)

    # Get available slave for processing task.
    def get_slave(self, task):
        # some algorithms will be filled in here.
        available_slaves = [w for w in self._slaves if w.doing_task is None]
        if not available_slaves:
            raise Exception("Not available Slaves.")
        import random
        slave = random.choice(available_slaves)
        return slave

    def find_slave(self, slave):
        if self.check_slave_existence(slave):
            return self._slaves[self._slaves.index(slave)]
        else:
            # error.
            raise ValueError("Non-existent Slave.")

    def start_heartbeat(self):

        def beat():

        self.caller = zmq.eventloop.ioloop.PeriodicCallback(self.beat, period, self.loop)
        self.caller.start()

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
                slave = slave_manager.get_slave(task)
                self.pop()
                slave.do_task(task)
                print("[*] Task Queue Size =", self.count())
            except Exception as err:
                print("[!]", err)

        except ValueError as err:
            print("[!]", err)


def communicate_with_client():
    address, empty, message = client_router.recv_multipart()
    client = Client(address)
    task = Task(message, client)
    task_queue.push(task)
    task_queue.process()

def communicate_with_slave():
    address, empty, message = slave_router.recv_multipart()

    slave = Slave(address)

    # will be modified.
    header = message[0:10]
    body = message[10:]

    if header == b'ready_____':
        try:
            slave_manager.add_slave(slave)
            print("[*] Slave {0} is ready!".format(slave.no))
            task_queue.process()
        except ValueError as err:
            print("[!]", err)

    elif header == b'finish____':
        real_slave = slave_manager.find_slave(slave)
        print("[*] Slave {0} is finished!".format(real_slave.no))
        task = real_slave.doing_task
        client = task.client
        client_router.send_multipart([client.addr, b'', body])
        real_slave.doing_task = None
        task_queue.process()

    elif header == b'exit______':
        raise NotImplementedError()

    else:
        raise ValueError("Unknown Message.")

# Prepare our context and sockets
context = zmq.Context()
client_router = context.socket(zmq.ROUTER)
slave_router = context.socket(zmq.ROUTER)
client_router.bind("tcp://*:5559")
slave_router.bind("tcp://*:5560")

# Initialize poll set
poller = zmq.Poller()
poller.register(client_router, zmq.POLLIN)
poller.register(slave_router, zmq.POLLIN)

task_queue = TaskQueue()
slave_manager = SlaveManager()

# Switch messages between sockets
while True:
    print("loop!")
    socks = dict(poller.poll())

    if socks.get(client_router) == zmq.POLLIN:
        print("[*] client_router pollin!")
        communicate_with_client()

    if socks.get(slave_router) == zmq.POLLIN:
        print("[*] slave_router pollin!")
        communicate_with_slave()