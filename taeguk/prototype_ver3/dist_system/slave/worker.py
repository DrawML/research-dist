import asyncio
import string
import random
from ..library import SingletonMeta


class WorkerToken(object):
    def __init__(self, token : bytes):
        self._token = token

    def __eq__(self, other : 'WorkerToken'):
        return self._token == other._token

    @staticmethod
    def generate_random_token(size : int = 512, chars : str = string.ascii_uppercase + string.digits) -> 'WorkerToken':
        # this must be modified!!
        raise NotImplementedError("This must be implemented!")
        return WorkerToken(''.join(random.choice(chars) for _ in range(size)))


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
    def __init__(self, addr, task):
        super().__init__(addr)
        self._task = task

    @property
    def task(self):
        return self._task


class WorkerManager(metaclass=SingletonMeta):

    def __init__(self):
        self._workers = []
        self._dic_token_task = {}
        self._dic_task_worker = {}

    @property
    def count(self):
        return len(self._workers)

    def add_token_task_to_dic(self, worker_token, task):
        if worker_token in self._dic_token_task:
            raise ValueError("Worker Token exists.")
        else:
            self._dic_token_task[worker_token] = task

    def add_worker(self, worker, worker_token):
        if self.check_worker_existence(worker):
            raise ValueError("Duplicated Worker.")
        elif not worker_token in self._dic_token_task:
            raise ValueError("Invalid Worker Token.")
        else:
            del self._dic_token_task[worker_token]
            self._workers.append(worker)
            self._dic_task_worker[worker.task] = worker

    def del_worker(self, worker_identity):
        worker = self._from_generic_to_worker(worker_identity)
        self._workers.remove(worker)
        del self._dic_task_worker[worker.task]

    def _from_generic_to_worker(self, identity_or_worker):
        if type(identity_or_worker) == WorkerIdentity:
            worker = self.find_worker(identity_or_worker)
        else:
            worker = identity_or_worker
        return worker

    def check_worker_existence(self, worker_identity, find_flag = False):
        targets = [worker for worker in self._workers if worker == worker_identity]
        ret = len(targets) > 0
        if find_flag:
            return (ret, targets)
        else:
            return ret

    def find_worker(self, worker_identity):
        exists, targets = self.check_worker_existence(worker_identity, find_flag=True)
        if exists:
            if len(targets) > 1:
                raise ValueError("Same Workers exist.")
            return targets[0]
        else:
            raise ValueError("Non-existent Worker.")

    def find_worker_having_task(self, task):
        try:
            self._dic_task_worker[task]
        except KeyError:
            raise ValueError("Non-existent Worker.")