import asyncio
import string
import random

def _id_generator(size=40, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class WorkerIdentity(object):

    _used_id = set()

    def __init__(self, id = None):
        if id is None:
            id = _id_generator()
            while id in WorkerIdentity._used_id:
                id = _id_generator()
            WorkerIdentity._used_id.add(id)
            self._fake_id = False
        else:
            self._fake_id = True
        self._id = id

    def __del__(self):
        if not self._fake_id:
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

        def _start(id, slave_addr, task):
            from multiprocessing import Process
            import multiprocessing
            #multiprocessing.set_start_method('spawn')
            Process(target=_worker_main, args=(id, slave_addr, task)).start()

        from concurrent.futures import ProcessPoolExecutor
        print("[Worker {0}] Create".format(self.id))
        _start(self.id, slave_addr, task)
        #executor = ProcessPoolExecutor()
        #loop = asyncio.get_event_loop()
        #asyncio.ensure_future(loop.run_in_executor(ProcessPoolExecutor(), _worker_main, self.id, slave_addr, task))
        #asyncio.ensure_future(_start(self.id, slave_addr, task))
        #yield from asyncio.sleep(10)
        print("***")

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

    print("_worker_main")

    import zmq
    from zmq.asyncio import Context, ZMQEventLoop
    import asyncio
    from ..common.task import SleepTaskResult
    from .task import SleepTask

    def _resolve_msg(msg):
        print(msg)
        #addr = msg[0]
        #assert msg[1] == b""
        header = msg[0]
        assert msg[1] == b""
        body = msg[2]

        return header, body

    def _dispatch_msg(header, body = b""):
        async def _dispatch_msg(msg):
            await socket.send_multipart(msg)

        msg = [id.encode(encoding='utf-8'), b'', header, b'', body]
        asyncio.ensure_future(_dispatch_msg(msg))

    def __dispatch_msg(header, body=b""):
        def _dispatch_msg(msg):
            socket.send_multipart(msg)

        msg = [id.encode(encoding='utf-8'), b'', header, b'', body]
        _dispatch_msg(msg)

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
            header, body = _resolve_msg(msg)
            # some codes will be filled later.
            break

    print("[Worker {0}] I'm created!".format(id))

    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    context = Context()
    socket = context.socket(zmq.DEALER)

    socket.connect(slave_addr)

    """
    policy = asyncio.get_event_loop_policy()
    policy.set_event_loop(policy.new_event_loop())
    loop = asyncio.get_event_loop()
    """

    loop.run_until_complete(_run_worker())



