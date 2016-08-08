import asyncio

class WorkerIdentity(object):

    def __init__(self, id = None):
        if id is None:
            id = WorkerIdentity._get_avail_id()
            self._fake_id = False
        else:
            self._fake_id = True
        self._id = id

    def __del__(self):
        if not self._fake_id:
            WorkerIdentity._id_pool.append(self._id)

    # I fire you if you override this.
    def __eq__(self, other):
        return self._id == other._id

    @property
    def id(self):
        return self._id

    @staticmethod
    @asyncio.coroutine
    def _generate_ids():
        for id in range(1, 100):
            yield id

    _id_gen = _generate_ids.__func__()
    _id_pool = []

    @staticmethod
    def _get_avail_id():
        if WorkerIdentity._id_pool:
            return WorkerIdentity._id_pool.pop(0)
        else:
            try:
                return next(WorkerIdentity._id_gen)
            except StopIteration:
                raise Exception("Can't allocate id to Worker.")


class Worker(WorkerIdentity):
    def __init__(self, tag = None):
        super().__init__()
        self._tag = tag

    def start(self, slave_addr, task):

        from multiprocessing import Process
        Process(target=_worker_main, args=(slave_addr, task)).start()

        self._task = task

    @staticmethod
    def make_worker_from_identity(worker_identity):
        return Worker(worker_identity.addr)

class WorkerManager(object):
    def __init__(self):
        self._workers = []

    @property
    def count(self):
        return len(self._workers)

    def add_worker(self, worker_identity):
        if self.check_worker_existence(worker_identity):
            raise ValueError("Duplicated Worker.")
        else:
            worker = Worker.make_worker_from_identity(worker_identity)
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


def _worker_main(slave_addr, task):
    pass