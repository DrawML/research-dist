#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import random
import string
from abc import *
from ..common import AutoIncrementEnum

class TaskType(AutoIncrementEnum):
    TYPE_SLEEP_TASK = ()
    #TYPE_TENSORFLOW_LEARNING = ()
    #TYPE_TENSORFLOW_TEST = ()


class TaskToken(object):
    def __init__(self, token : bytes):
        self._token = token

    def __eq__(self, other : 'TaskToken'):
        return self._token == other._token

    @staticmethod
    def generate_random_token(size : int = 512, chars : str = string.ascii_uppercase + string.digits) -> 'TaskToken':
        # this must be modified!!
        raise NotImplementedError("This must be implemented!")
        return TaskToken(''.join(random.choice(chars) for _ in range(size)))


class Task(metaclass = ABCMeta):
    def __init__(self, task_token : TaskToken):
        self._task_token = task_token

    def __eq__(self, other : 'Task'):
        return self._task_token == other._task_token

    @property
    def task_token(self):
        return self._task_token

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class TaskJob(metaclass = ABCMeta):
    @abstractmethod
    def to_bytes(self):
        pass

    @abstractstaticmethod
    def from_bytes(bytes : bytes) -> 'TaskJob':
        pass


class TaskResult(metaclass = ABCMeta):
    @abstractmethod
    def to_bytes(self):
        pass

    @abstractstaticmethod
    def from_bytes(bytes: bytes) -> 'TaskResult':
        pass