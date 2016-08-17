from ..library import (AutoIncrementEnum, SingletonMeta)
from ..task.task import *


class TaskStatus(AutoIncrementEnum):
    STATUS_REGISTERED = ()
    STATUS_PROCESSING = ()
    STATUS_COMPLETE = ()


class TaskManager(CommonTaskManager, metaclass=SingletonMeta):

    def __init__(self):
        self._all_tasks = []
        self._registered_tasks = []
        self._processing_tasks = []
        self._complete_tasks = []
        self._dic_status_queue = {
            TaskStatus.STATUS_REGISTERED : self._registered_tasks,
            TaskStatus.STATUS_PROCESSING : self._processing_tasks,
            TaskStatus.STATUS_COMPLETE : self._complete_tasks
        }
        super().__init__(self._dic_status_queue, TaskStatus.STATUS_REGISTERED)

    def cancel_task(self, task_token_or_task):
        task = self._from_generic_to_task(task_token_or_task)
        self.del_task(task)

    @property
    def registered_tasks(self):
        return tuple(self._registered_tasks)

    @property
    def complete_tasks(self):
        return tuple(self._complete_tasks)