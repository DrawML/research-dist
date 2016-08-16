class ResultReceiverAddress(object):
    def __init__(self, type_ : str, ip : str, port : int):
        assert type_ == 'tcp'
        self._type = type_
        self._ip = ip
        self._port = port

    def to_dict(self):
        return {
            'type' : self._type,
            'ip' : self._ip,
            'port' : self._port
        }