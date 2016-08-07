class SlaveIdentity(object):
    def __init__(self, addr):
        self._addr = addr

    # I fire you if you override this.
    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Slave(SlaveIdentity):
    def __init__(self, addr, tag = None):
        super().__init__(addr)
        self._tag = tag
        self._tasks = []

    @property
    def tag(self):
        return self._tag

    @property
    def tasks_count(self):
        return len(self._tasks)

    def assign_task(self, task):
        self._tasks.append(task)

    def delete_task(self, task_identity):
        self._tasks.remove(task_identity)

    @staticmethod
    def make_slave_from_identity(slave_identity):
        return Slave(slave_identity.addr)


class SlaveManager(object):
    def __init__(self):
        self._slaves = []

    @property
    def count(self):
        return len(self._slaves)

    def add_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            raise ValueError("Duplicated Slave.")
        else:
            slave = Slave.make_slave_from_identity(slave_identity)
            self._slaves.append(slave)

    def del_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            slave = self.find_slave(slave_identity)
            self._slaves.remove(slave)
        else:
            raise ValueError("Non-existent Slave.")

    def check_slave_existence(self, slave_identity):
        return slave_identity in self._slaves

    def find_slave(self, slave_identity):
        if self.check_slave_existence(slave_identity):
            return self._slaves[self._slaves.index(slave_identity)]
        else:
            raise ValueError("Non-existent Slave.")

    # Get proper slave for task.
    def get_proper_slave(self, task):

        # some algorithms will be filled in here.
        proper_slave = None
        for slave in self._slaves:
            if slave.tasks_count() >= 3:
                continue
            if proper_slave is None or proper_slave.tasks_count() < slave.tasks_count():
                proper_slave = slave

        if proper_slave is None:
            raise Exception("Not available Slaves.")
        else:
            return proper_slave