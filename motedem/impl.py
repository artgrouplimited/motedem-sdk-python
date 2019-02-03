from bluepy import btle


class __event__:
    def __init__(self):
        self.__delegate_key__ = int(0)
        self.__delegates__ = dict()

    def invoke(self, *args, **kwargs):
        for _, v in self.__delegates__.items():
            v(*args, **kwargs)

    def add(self, delegate)->int:
        self.__delegate_key__ += 1
        key = self.__delegate_key__
        self.__delegates__[key] = delegate
        return key

    def remove(self, key: int)->None:
        del self.__delegates__[key]


class __peripheral_delegate__(btle.DefaultDelegate):
    def __init__(self, device):
        self.__device__ = device
        self.__data_notify__ = __event__()
        self.__control_notify__ = __event__()

    def handleNotification(self, cHandle: int, data: bytes):
        if self.__device__.__data_notify__.getHandle() == cHandle:
            self.__data_notify__.invoke(data)
        elif self.__device__.__control_notify__.getHandle() == cHandle:
            self.__control_notify__.invoke(data)

    def dataNotify(self, handler_or_key):
        if type(handler_or_key) is int:
            self.__data_notify__.remove(handler_or_key)
        else:
            return self.__data_notify__.add(handler_or_key)

    def controlNotify(self, handler_or_key):
        if type(handler_or_key) is int:
            self.__control_notify__.remove(handler_or_key)
        else:
            return self.__control_notify__.add(handler_or_key)


class __handler_remover__:
    def __init__(self, revoker, handler):
        self.__revoker__ = revoker
        self.__handler__ = handler

    def __enter__(self):
        self.__key__ = self.__revoker__(self.__handler__)

    def __exit__(self, *args):
        self.__revoker__(self.__key__)


class __reference__:
    def __init__(self, value=None):
        self.__value__ = value

    def get(self):
        return self.__value__

    def put(self, value):
        self.__value__ = value
