from .task import *


class SleepTask(Task):
    def __init__(self, job : SleepTaskJob):
        assert isinstance(job, SleepTaskJob)
        super().__init__()
        self._job = job

    @property
    def job(self):
        return self._job

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result : SleepTaskResult):
        assert isinstance(result, SleepTaskResult)
        self._result = result


class SleepTaskJob(TaskJob):
    def __init__(self, seconds : int):
        super().__init__()
        self._seconds = seconds

    def to_bytes(self) -> bytes:
        return self._seconds.to_bytes(4, byteorder='big')

    @staticmethod
    def from_bytes(bytes : bytes) -> 'SleepTaskJob':
        return SleepTaskJob(int.from_bytes(bytes[0:4], byteorder='big'))

    @property
    def seconds(self):
        return self._seconds


class SleepTaskResult(TaskResult):
    def __init__(self, comment : str):
        super().__init__()
        self._comment = comment

    def to_bytes(self) -> bytes:
        return self._comment.encode(encoding='utf-8')

    @staticmethod
    def from_bytes(bytes : bytes) -> 'SleepTaskResult':
        return SleepTaskResult(bytes.decode(encoding='utf-8'))

    @property
    def comment(self):
        return self._comment