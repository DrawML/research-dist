#!/usr/bin/python3
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio


class ClientIdentity(object):
    def __init__(self, addr):
        self._addr = addr

    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Client(ClientIdentity):

        def __init__(self, addr):
            super().__init__(addr)
            self._tasks = []

        def have_task(self, task):
            self._tasks.append(task)

        def lose_task(self, task_identity):
            self._tasks.remove(task_identity)

        @staticmethod
        def make_client_from_identity(client_identity):
            return Client(client_identity.addr)


class ClientManager(object):

    def __init__(self):
        self._clients = []

    @property
    def count(self):
        return len(self._clients)

    def add_client(self, client_identity):
        if self.check_client_existence(client_identity):
            raise ValueError("Duplicated Client.")
        else:
            client = Client.make_client_from_identity(client_identity)
            self._clients.append(client)

    def del_client(self, client_identity):
        if self.check_client_existence(client_identity):
            client = self.find_client(client_identity)
            self._clients.remove(client)
        else:
            raise ValueError("Non-existent Client.")

    def check_client_existence(self, client_identity):
        return client_identity in self._clients

    def find_client(self, client_identity):
        if self.check_client_existence(client_identity):
            return self._clients[self._clients.index(client_identity)]
        else:
            raise ValueError("Non-existent Client.")


class SlaveIdentity(object):
    def __init__(self, addr):
        self._addr = addr

    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Slave(SlaveIdentity):
    def __init__(self, addr, tag = None):
        super().__init__(addr)
        self._tag = tag
        self._tasks = []

    @property
    def tag(self):
        return self._tag

    @property
    def tasks_count(self):
        return len(self._tasks)

    def assign_task(self, task):
        self._tasks.append(task)

    def delete_task(self, task_identity):
        self._tasks.remove(task_identity)

    @staticmethod
    def make_slave_from_identity(slave_identity):
        return Slave(slave_identity.addr)


class SlaveManager(object):
    def __init__(self):
        self._slaves = []

    @property
    def count(self):
        return len(self._slaves)

    def add_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            raise ValueError("Duplicated Slave.")
        else:
            slave = Slave.make_slave_from_identity(slave_identity)
            self._slaves.append(slave)

    def del_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            slave = self.find_slave(slave_identity)
            self._slaves.remove(slave)
        else:
            raise ValueError("Non-existent Slave.")

    def check_slave_existence(self, slave_identity):
        return slave_identity in self._slaves

    def find_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            return self._slaves[self._slaves.index(slave_identity)]
        else:
            raise ValueError("Non-existent Slave.")

    # Get available slave for processing task.
    def get_slave(self, task):
        # some algorithms will be filled in here.
        available_slaves = [w for w in self._slaves if w.doing_task is None]
        if not available_slaves:
            raise Exception("Not available Slaves.")
        import random
        slave = random.choice(available_slaves)
        return slave


class TaskIdentity(object):

    def __init__(self, id = None):
        if id is None:
            id = TaskIdentity._get_avail_id()
            self._fake_id = False
        else:
            self._fake_id = True
        self._id = id

    def __del__(self):
        if not self._fake_id:
            TaskIdentity._id_pool.append(self._id)

    def __eq__(self, other):
        return self._id == other._id

    @property
    def id(self):
        return self._id

    @staticmethod
    @asyncio.coroutine
    def _generate_ids():
        for id in range(1, 100000):
            yield id

    _id_gen = _generate_ids.__func__()
    _id_pool = []

    @staticmethod
    def _get_avail_id():
        if TaskIdentity._id_pool:
            return TaskIdentity._id_pool.pop(0)
        else:
            try:
                return next(TaskIdentity._id_gen)
            except StopIteration:
                raise Exception("Can't allocate id to Task.")


class Task(TaskIdentity):

    STATUS_NO_REGISTERED = 0
    STATUS_WAITING = 1
    STATUS_PROCESSING = 2
    STATUS_COMPLETE = 3

    def __init__(self, client, req_id, tag = None):
        super().__init__()
        self._client = client
        self._req_id = req_id
        self._tag = tag
        self._status = Task.STATUS_NO_REGISTERED

    @property
    def client(self):
        return self._client

    @property
    def req_id(self):
        return self._req_id

    @property
    def tag(self):
        return self._tag

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def result(self):
        raise NotImplementedError("This function must be override.")

    @result.setter
    def result(self, result):
        raise NotImplementedError("This function must be override.")


class SleepTask(Task):
    def __init__(self, seconds, client, req_id, tag = None):
        super().__init__(client, req_id, tag)
        self._seconds = seconds

    @property
    def seconds(self):
        return self._seconds

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result


class TaskManager(object):

    def __init__(self):
        self._all_tasks = []
        self._waiting_tasks = []
        self._processing_tasks = []
        self._complete_tasks = []
        self._dic_queue = {
            Task.STATUS_WAITING : self._waiting_tasks,
            Task.STATUS_PROCESSING : self._processing_tasks,
            Task.STATUS_COMPLETE : self._complete_tasks
        }

    def add_task(self, task):
        task.status = Task.STATUS_WAITING
        self._all_tasks.append(task)
        self._waiting_tasks.append(task)

    def del_task(self, task_identity):
        if self.check_task_existence(task_identity):
            task = self.find_task(task_identity)
            self._dic_queue[task.status].remove(task)
        else:
            raise ValueError("Non-existent Task.")

    def change_task_status(self, task_identity, new_status):
        if self.check_task_existence(task_identity):
            task = self.find_task(task_identity)
            cur_status = task.status
            self._dic_queue[cur_status].remove(task)
            self._dic_queue[new_status].append(task)
            task.status = new_status

    def check_task_existence(self, task_identity):
        return task_identity in self._all_tasks

    def find_task(self, task_identity):
        if self.check_task_existence(task_identity):
            return self._all_tasks[self._all_tasks.index(task_identity)]
        else:
            raise ValueError("Non-existent Task.")

    def report_complete_tasks(self):
        for task in self._complete_tasks:
            client = task.client
            reply_body = task.req_id.to_bytes(4, byteorder='big')
            reply_body += task.result   # conversion is needed.
            client.lose_task(task)
            client_router.dispatch_msg(client.addr, b"TaskFinish", reply_body)
            self._all_tasks.remove(task)
        self._complete_tasks.clear()




class ClientRouter(object):

    def __init__(self, context, addr):
        self._context = context
        self._addr = addr
        pass

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            msg = await self._router.recv_multipart()
            await self._process(msg)

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        client_identity = ClientIdentity(addr)

        if header == "Register":
            client_manager.add_client(client_identity)

        elif header == "SleepTask":
            client = client_manager.find_client(client_identity)

            req_id = int.from_bytes(body[0:4])
            seconds = int.from_bytes(body[4:8])
            task = SleepTask(seconds, client, req_id)

            reply_body = req_id.to_bytes(4, byteorder='big')
            self.dispatch_msg(client.addr, b"TaskAccept", reply_body)

            client.have_task(task)
            task_manager.add_task(task)
            scheduler.invoke()

        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(self, msg):
        addr = msg[0]
        assert msg[1] == b""
        header = msg[2]
        assert msg[3] == b""
        body = msg[4]

        return addr, header, body

    def dispatch_msg(self, addr, header, body):

        async def _dispatch_msg(self, msg):
            await self._router.send_multipart(msg)

        msg = [addr, b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class SlaveRouter(object):
    def __init__(self, context, addr):
        self._context = context
        self._addr = addr

    async def run(self):
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(self._addr)

        while True:
            msg = await self._router.recv_multipart()
            await self._process()

    async def _process(self, msg):
        addr, header, body = self._resolve_msg(msg)

        slave_identity = SlaveIdentity(addr)

        if header == "Register":
            slave_manager.add_slave(slave_identity)
            scheduler.invoke()

        elif header == "TaskFinish":
            task_id = int.from_bytes(body[0:4])
            task_result = int.from_bytes(body[4:])

            task_identity = TaskIdentity(task_id)
            task_manager.find_task(task_identity).result = task_result      # conversion is needed.

            slave = slave_manager.find_slave(slave_identity)
            slave.delete_task(task_identity)

            task_manager.change_task_status(task_identity, Task.STATUS_COMPLETE)
            scheduler.invoke()

        else:
            raise ValueError("Invalid Header.")

    def _resolve_msg(msg):
        addr = msg[0]
        assert msg[1] == b""
        header = msg[2]
        assert msg[3] == b""
        body = msg[4]

        return addr, header, body

    def dispatch_msg(self, addr, header, body):

        async def _dispatch_msg(self, msg):
            await self._router.send_multipart(msg)

        msg = [addr, b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))


class Scheduler(object):

    def __init__(self):
        pass

    def invoke(self):
        # 1. 현재 waiting하고 있는 task가 있는 지 보고 available한 slave 있는지 판단하여 task를 slave에 배치한다.
        # 2. 다 처리된 task가 있으면 client에 보고 한다.
        self._assign_waiting_task_to_slave()
        self._report_complete_task_to_client()

    def _assign_waiting_task_to_slave(self):
        pass

    def _report_complete_task_to_client(self):
        task_manager.report_complete_tasks()


CLIENT_ROUTER_ADDR = 'tcp://127.0.0.1:5555'
SLAVE_ROUTER_ADDR = 'tcp://127.0.0.1:5556'
CONTROL_ROUTER_ADDR = 'tcp://127.0.0.1:5000'

context = Context()
client_router = ClientRouter(context, CLIENT_ROUTER_ADDR)
slave_router = SlaveRouter(context, SLAVE_ROUTER_ADDR)

client_manager = ClientManager()
task_manager = TaskManager()
slave_manager = SlaveManager()
scheduler = Scheduler()

async def run_server():
    asyncio.ensure_future(client_router.run())
    asyncio.ensure_future(slave_router.run())

    # terminate server if receive a control packet from control socket.
    control_router = context.socket(zmq.ROUTER)
    control_router.bind(CONTROL_ROUTER_ADDR)
    msg = await control_router.recv_multipart()


def main():
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')
        sys.exit(0)


if __name__ == '__main__':
    main()