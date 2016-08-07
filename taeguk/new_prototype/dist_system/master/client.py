class ClientIdentity(object):
    def __init__(self, addr):
        self._addr = addr

    # I fire you if you override this.
    def __eq__(self, other):
        return self._addr == other._addr

    @property
    def addr(self):
        return self._addr


class Client(ClientIdentity):

        def __init__(self, addr):
            super().__init__(addr)
            self._tasks = []

        def have_task(self, task):
            self._tasks.append(task)

        def lose_task(self, task_identity):
            self._tasks.remove(task_identity)

        @staticmethod
        def make_client_from_identity(client_identity):
            return Client(client_identity.addr)


class ClientManager(object):

    def __init__(self):
        self._clients = []

    @property
    def count(self):
        return len(self._clients)

    def add_client(self, client_identity):
        if self.check_client_existence(client_identity):
            raise ValueError("Duplicated Client.")
        else:
            client = Client.make_client_from_identity(client_identity)
            self._clients.append(client)

    def del_client(self, client_identity):
        if self.check_client_existence(client_identity):
            client = self.find_client(client_identity)
            self._clients.remove(client)
        else:
            raise ValueError("Non-existent Client.")

    def check_client_existence(self, client_identity):
        return client_identity in self._clients

    def find_client(self, client_identity):
        if self.check_client_existence(client_identity):
            return self._clients[self._clients.index(client_identity)]
        else:
            raise ValueError("Non-existent Client.")