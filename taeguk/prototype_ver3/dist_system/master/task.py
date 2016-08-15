from enum import Enum
from ..task.task import *


class TaskStatus(AutoIncrementEnum):
    STATUS_PENDING_ACK = ()
    STATUS_WAITING = ()
    STATUS_PROCESSING = ()
    STATUS_COMPLETE = ()


class TaskManager(object):

    def __init__(self):
        self._all_tasks = []
        self._pending_ack_tasks = []
        self._waiting_tasks = []
        self._processing_tasks = []
        self._complete_tasks = []
        self._dic_queue = {
            TaskStatus.STATUS_PENDING_ACK : self._pending_ack_tasks,
            TaskStatus.STATUS_WAITING : self._waiting_tasks,
            TaskStatus.STATUS_PROCESSING : self._processing_tasks,
            TaskStatus.STATUS_COMPLETE : self._complete_tasks
        }

    def add_task(self, task):
        if self.check_task_existence(task.task_token):
            raise ValueError("Duplicated Task.")
        else:
            task.status = TaskStatus.STATUS_PENDING_ACK
            self._waiting_tasks.append(task)
            self._all_tasks.append(task)

    def del_task(self, task_token_or_task):
        task = self._from_generic_to_task(task_token_or_task)
        self._dic_queue[task.status].remove(task)
        self._all_tasks.remove(task)

    def _from_generic_to_task(self, task_token_or_task):
        if isinstance(task_token_or_task, TaskToken):
            task = self.find_task(task_token_or_task)
        else:
            task = task_token_or_task
        return task

    def change_task_status(self, task_token_or_task, new_status):
        task = self._from_generic_to_task(task_token_or_task)
        cur_status = task.status
        self._dic_queue[cur_status].remove(task)
        self._dic_queue[new_status].append(task)
        task.status = new_status

    def check_task_existence(self, task_token, find_flag = False):
        targets = [task for task in self._all_tasks if task.task_token == task_token]
        ret = len(targets) > 0
        if find_flag:
            return (ret, targets)
        else:
            return ret

    def find_task(self, task_token):
        exists, targets = self.check_task_existence(task_token, find_flag=True)
        if exists:
            if len(targets) > 1:
                raise ValueError("Same Tasks exist.")
            return targets[0]
        else:
            raise ValueError("Non-existent Task.")

    @property
    def waiting_tasks(self):
        return tuple(self._waiting_tasks)

    @property
    def complete_tasks(self):
        return tuple(self._complete_tasks)