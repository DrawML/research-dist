import asyncio
from ..protocol import ResultReceiverAddress
from ..task.task import *


class TaskInformation(object):

    def __init__(self, result_receiver_address, task_token, task_type, task):
        self._result_receiver_address = result_receiver_address
        self._task_token = task_token
        self._task_type = task_type
        self._task = task

    @property
    def result_receiver_address(self):
        return self._result_receiver_address

    @property
    def task_token(self):
        return self._task_token

    @property
    def task_type(self):
        return self._task_type

    @property
    def task(self):
        return self._task

    @staticmethod
    def from_bytes(bytes_ : bytes) -> 'TaskInformation':
        TaskInformation("""will be filled...""")


async def do_task(task_info : TaskInformation):

    if task_info.task_type == TaskType.TYPE_SLEEP_TASK:
        await asyncio.sleep(task_info.task.seconds)
    else:
        raise ValueError("Invalid Task Type.")

    """
    tensorflow 관련 task 실행시킬 땐,
    asyncio.create_subprocess_exec()
    subprocess.wait()
    활용하자.
    """