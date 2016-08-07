from ..common.task import *

class Task(TaskIdentity):

    STATUS_NOT_REGISTERED = 0
    STATUS_WAITING = 1
    STATUS_PROCESSING = 2
    STATUS_COMPLETE = 3

    def __init__(self, client, req_id, tag = None):
        super().__init__()
        self._client = client
        self._req_id = req_id
        self._tag = tag
        self._status = Task.STATUS_NOT_REGISTERED

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
    def job(self):
        raise NotImplementedError("This function must be override.")

    @job.setter
    def job(self, job):
        raise NotImplementedError("This function must be override.")

    @property
    def result(self):
        raise NotImplementedError("This function must be override.")

    @result.setter
    def result(self, result):
        raise NotImplementedError("This function must be override.")

    def set_result_from_bytes(self, bytes):
        raise NotImplementedError("This function must be override.")


class SleepTask(Task):
    def __init__(self, job, client, req_id, tag = None):
        super().__init__(client, req_id, tag)
        self._job = job

    @property
    def seconds(self):
        return self._seconds

    @property
    def job(self):
        return self._job

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result : SleepTaskJob):
        self._result = result

    def set_result_from_bytes(self, bytes):
        self.result = SleepTaskResult.from_bytes(bytes)


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

    @property
    def waiting_tasks(self):
        return tuple(self._waiting_tasks)

    @property
    def complete_tasks(self):
        return tuple(self._complete_tasks)