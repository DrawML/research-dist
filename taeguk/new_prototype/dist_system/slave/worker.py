import asyncio
import string
import random

def _id_generator(size=40, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class WorkerIdentity(object):

    _used_id = set()

    def __init__(self):
        id = _id_generator()
        while id in WorkerIdentity._used_id:
            id = _id_generator()
        WorkerIdentity._used_id.add(id)
        self._id = id

    def __del__(self):
        WorkerIdentity._used_id.remove(self._id)

    # I fire you if you override this.
    def __eq__(self, other):
        return self._id == other._id

    @property
    def id(self):
        return self._id


class Worker(WorkerIdentity):

    STATUS_CREATED = 0
    STATUS_WORKING = 1
    STATUS_FINISHED = 2

    def __init__(self, tag = None):
        super().__init__()
        self._tag = tag
        self._status = Worker.STATUS_CREATED

    def start(self, slave_addr, task):
        self._task = task

        from multiprocessing import Process
        Process(target=_worker_main, args=(self.id, slave_addr, task)).start()

    @property
    def task(self):
        return self._task

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class WorkerManager(object):
    def __init__(self):
        self._workers = []

    @property
    def count(self):
        return len(self._workers)

    def add_worker(self, worker):
        if self.check_worker_existence(worker):
            raise ValueError("Duplicated Worker.")
        else:
            self._workers.append(worker)

    def del_worker(self, worker_identity):
        if self.check_worker_existence(worker_identity):
            worker = self.find_worker(worker_identity)
            self._workers.remove(worker)
        else:
            raise ValueError("Non-existent Worker.")

    def check_worker_existence(self, worker_identity):
        return worker_identity in self._workers

    def find_worker(self, worker_identity):
        if self.check_worker_existence(worker_identity):
            return self._workers[self._workers.index(worker_identity)]
        else:
            raise ValueError("Non-existent Worker.")


def _worker_main(id, slave_addr, task):

    import zmq
    from zmq.asyncio import Context, ZMQEventLoop
    import asyncio
    from ..common.task import SleepTaskResult
    from .task import SleepTask

    def _resolve_msg(self, msg):
        addr = msg[0]
        assert msg[1] == b""
        header = msg[2]
        assert msg[3] == b""
        body = msg[4]

        return addr, header, body

    def _dispatch_msg(header, body):
        async def _dispatch_msg(msg):
            await socket.send_multipart(msg)

        msg = [slave_addr, b'', id.encode(encoding='utf-8'), b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))

    def _process_sleep_task(task):
        async def __process_sleep_task(task):
            await asyncio.sleep(task.job.seconds)
            task.result = SleepTaskResult("Sleep " + str(task.job.seconds) + "By " + id)
            _dispatch_msg(b"TaskFinish", task.result.to_bytes())

        asyncio.ensure_future(__process_sleep_task(task))

    async def _run_worker():
        _dispatch_msg(b"TaskStart")
        if isinstance(task, SleepTask):
            _process_sleep_task(task)
        else:
            raise ValueError("Invalid Task Type.")

        while True:
            msg = await socket.recv_multipart()
            addr, header, body = _resolve_msg(msg)
            # some codes will be filled later.
            break

    context = Context()
    socket = context.socket(zmq.ROUTER)
    socket.connect(slave_addr)

    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_run_worker())



