#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import asyncio


###################### Task Identity #######################

class TaskIdentity(object):

    def __init__(self, id = None, group = None):
        if id is None:
            id = TaskIdentity._get_avail_id()
            self._fake_id = False
        else:
            self._fake_id = True
        self._id = id
        self._group = group

    def __del__(self):
        if not self._fake_id:
            TaskIdentity._id_pool.append(self._id)

    # I fire you if you override this.
    def __eq__(self, other):
        return self._group == other._group and self._id == other._id

    @property
    def id(self):
        return self._id

    @staticmethod
    @asyncio.coroutine
    def _generate_ids():
        for id in range(1, 100000):
            yield id

    _id_gen = _generate_ids.__func__()
    _id_pool = []

    @staticmethod
    def _get_avail_id():
        if TaskIdentity._id_pool:
            return TaskIdentity._id_pool.pop(0)
        else:
            try:
                return next(TaskIdentity._id_gen)
            except StopIteration:
                raise Exception("Can't allocate id to Task.")

    def to_bytes(self):
        self._id.to_bytes(4, byteorder='big')




###################### Task Job and Result #######################

class TaskJob(object):
    def to_bytes(self):
        raise NotImplementedError("This function must be override.")

    @staticmethod
    def from_bytes(bytes):
        raise NotImplementedError("This function must be override.")


class TaskResult(object):
    def to_bytes(self):
        raise NotImplementedError("This function must be override.")

    @staticmethod
    def from_bytes(bytes):
        raise NotImplementedError("This function must be override.")




###################### Sleep Task Job and Result #######################

class SleepTaskJob(TaskJob):
    def __init__(self, seconds : int):
        super().__init__()
        self._seconds = seconds

    def to_bytes(self) -> bytes:
        return self._seconds.to_bytes(4, byteorder='big')

    @staticmethod
    def from_bytes(bytes : bytes) -> 'SleepTaskJob':
        return SleepTaskJob.__init__(int.from_bytes(bytes[0:4], byteorder='big'))


class SleepTaskResult(TaskResult):
    def __init__(self, comment : str):
        super().__init__()
        self._comment = comment

    def to_bytes(self) -> bytes:
        return self._comment.encode(encoding='utf-8')

    @staticmethod
    def from_bytes(bytes : bytes) -> 'SleepTaskResult':
        return SleepTaskResult.__init__(bytes.decode(encoding='utf-8'))