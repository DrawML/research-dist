from ..common.task import *

class Task(TaskIdentity):

    def __init__(self, id, tag = None):
        super().__init__(id, group="MasterRequest")
        self._tag = tag

    @property
    def tag(self):
        return self._tag

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
    def __init__(self, job, id, tag = None):
        super().__init__(id, tag)
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