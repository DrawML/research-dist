#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import random
import string
from abc import *
from ..library import AutoIncrementEnum
from ..protocol import ResultReceiverAddress


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
    def __init__(self, task_token : TaskToken, result_receiver_address : ResultReceiverAddress):
        self._task_token = task_token
        self._result_receiver_address = result_receiver_address

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

    @property
    @abstractmethod
    def job(self):
        pass

    @property
    @abstractmethod
    def result(self):
        pass

    @result.setter
    @abstractmethod
    def result(self, result):
        pass


class TaskJob(metaclass = ABCMeta):
    @abstractmethod
    def to_bytes(self):
        pass

    @staticmethod
    @abstractmethod
    def from_bytes(bytes_ : bytes) -> 'TaskJob':
        pass


class TaskResult(metaclass = ABCMeta):
    @abstractmethod
    def to_bytes(self):
        pass

    @staticmethod
    @abstractmethod
    def from_bytes(bytes_: bytes) -> 'TaskResult':
        pass