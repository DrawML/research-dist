class WorkerIdentity(object):
    def __init__(self, addr):
        self._addr = addr

    # I fire you if you override this.
    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Worker(WorkerIdentity):
    def __init__(self, addr, tag = None):
        super().__init__(addr)
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