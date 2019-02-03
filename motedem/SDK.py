from .impl import __event__, __peripheral_delegate__, __handler_remover__, __reference__

class InvalidArgument(Exception):
    def __init__(self):
        super().__init__()

class Device:
    __motedem_service__ = 'd6c12900-95e7-11e6-ae22-56b6b6499611'
    __motedem_data_write__ = 'd6c12804-95e7-11e6-ae22-56b6b6499611'
    __motedem_data_notify__ = 'd6c12805-95e7-11e6-ae22-56b6b6499611'
    __motedem_control_write__ = 'd6c12806-95e7-11e6-ae22-56b6b6499611'
    __motedem_control_notify__ = 'd6c12807-95e7-11e6-ae22-56b6b6499611'

    def __init__(self, peripheral):
        self.__notify_handler__ = __peripheral_delegate__(self)
        self.__data_notify_key__ = self.__notify_handler__.dataNotify(self.__on_data_notify__)
        self.__temperature_changed_handler__ = __event__()
        self.__peripheral__ = peripheral
        service = self.__peripheral__.getServiceByUUID(Device.__motedem_service__)
        self.__data_write__ = service.getCharacteristics(Device.__motedem_data_write__)[0]
        self.__data_notify__ = service.getCharacteristics(Device.__motedem_data_notify__)[0]
        self.__control_write__ = service.getCharacteristics(Device.__motedem_control_write__)[0]
        self.__control_notify__ = service.getCharacteristics(Device.__motedem_control_notify__)[0]
        self.__peripheral__.withDelegate(self.__notify_handler__)
        self.__peripheral__.writeCharacteristic(1 + self.__data_notify__.getHandle(), b'\x01\x00')
        self.__peripheral__.writeCharacteristic(1 + self.__control_notify__.getHandle(), b'\x01\x00')

    def readTemperature(self)->float:
        control_sequence = b'\x01'
        data_sequence = b'\x45\x34\x71\x04\xee'
        control_value = __reference__()
        data_value = __reference__()
        def controlNotify(data:bytes):
            control_value.put(data)
        def dataNotify(data:bytes):
            if 0x71 == data[0]:
                data_value.put(data)
        with\
            __handler_remover__(self.__notify_handler__.controlNotify, controlNotify),\
            __handler_remover__(self.__notify_handler__.dataNotify, dataNotify):
            self.__control_write__.write(control_sequence, True)
            self.__data_write__.write(data_sequence, True)
            while not(control_value.get() and data_value.get()):
                self.__peripheral__.waitForNotifications(0.1)
        if 1 != len(control_value.get()) or 0x01 != control_value.get()[0]:
            raise InvalidArgument()
        if 6 != len(data_value.get()) or 0x05 != data_value.get()[1] or 0x30 < data_value.get()[2]:
            raise InvalidArgument()
        result = float((int(data_value.get()[3] & 0xf) << 8) | data_value.get()[4]) * 0.0625
        return result

    def learnAC(self, ready_callback = None):
        return self.__learn_common__(0x27, ready_callback)

    def learnAV(self, ready_callback = None):
        return self.__learn_common__(0x24, ready_callback)

    def emit(self, sequence):
        length = len(sequence)
        if 1 > length:
            raise InvalidArgument()
        buffer = bytearray()
        buffer += b'\x45\x34\x25' + bytes([5 + length]) + b'\x81'
        buffer += sequence
        buffer += bytes([sum(buffer)])
        packet_count = int((len(buffer) + 19) / 20)
        control_sequence = bytes([packet_count])
        control_value = __reference__()
        data_value = __reference__()
        def controlNotify(data:bytes):
            control_value.put(data)
        def dataNotify(data:bytes):
            if 0x25 == data[0]:
                data_value.put(data)
        with\
            __handler_remover__(self.__notify_handler__.controlNotify, controlNotify),\
            __handler_remover__(self.__notify_handler__.dataNotify, dataNotify):
            self.__control_write__.write(control_sequence, True)
            while len(buffer):
                self.__data_write__.write(buffer[:20], True)
                buffer = buffer[20:]
            while not(control_value.get() and data_value.get()):
                self.__peripheral__.waitForNotifications(0.1)
        if 1 != len(control_value.get()) or 0x01 != control_value.get()[0]:
            raise InvalidArgument()
        if 4 != len(data_value.get()) or 0x03 != data_value.get()[1] or 0x30 < data_value.get()[2]:
            raise InvalidArgument()
        pass

    def onTemperatureReport(self, handler_or_key):
        if type(handler_or_key) is int:
            self.__temperature_changed_handler__.remove(handler_or_key)
        else:
            return self.__temperature_changed_handler__.add(handler_or_key)

    def __enter__(self):
        self.__peripheral__.__enter__()
        return self

    def __exit__(self, *l, **d):
        self.__peripheral__.withDelegate(None).__exit__(*l, **d)
        del self.__control_notify__
        del self.__control_write__
        del self.__data_notify__
        del self.__data_write__
        del self.__peripheral__
        self.__notify_handler__.dataNotify(self.__data_notify_key__)
        del self.__temperature_changed_handler__
        del self.__notify_handler__

    def __on_data_notify__(self, data):
        if (6 == len(data)) and (0x71 == data[0]) and (0x05 == data[1]) and (0x30 >= data[2]):
            value = float((int(data[3] & 0xf) << 8) | data[4]) * 0.0625
            self.__temperature_changed_handler__.invoke(self, value)

    def __learn_common__(self, opcode, ready_callback):
        control_sequence = b'\x01'
        data_sequence = b'\x45\x34' + bytes([opcode]) + b'\x04'
        data_sequence += bytes([sum(data_sequence)])
        control_value = __reference__()
        data_value = __reference__()
        def controlNotify(data:bytes):
            control_value.put(data)
        def dataNotify(data:bytes):
            if opcode == data[0]:
                data_value.put(data)
        with\
            __handler_remover__(self.__notify_handler__.controlNotify, controlNotify),\
            __handler_remover__(self.__notify_handler__.dataNotify, dataNotify):
            self.__control_write__.write(control_sequence, True)
            self.__data_write__.write(data_sequence, True)
            while not(control_value.get() and data_value.get()):
                self.__peripheral__.waitForNotifications(0.1)
        if 1 != len(control_value.get()) or 0x01 != control_value.get()[0]:
            raise InvalidArgument()
        if 4 != len(data_value.get()) or 0x03 != data_value.get()[1] or 0x30 < data_value.get()[2]:
            raise InvalidArgument()
        if ready_callback:
            ready_callback(sender = self)
        control_value = __reference__()
        data_value = list()
        def controlNotify(data:bytes):
            control_value.put(data)
        def dataNotify(data:bytes):
            if len(data_value) or (opcode == data[0]):
                data_value.append(data)
        with\
            __handler_remover__(self.__notify_handler__.controlNotify, controlNotify),\
            __handler_remover__(self.__notify_handler__.dataNotify, dataNotify):
            while not(control_value.get() and control_value.get()[0] <= len(data_value)):
                self.__peripheral__.waitForNotifications(0.1)
        initial_response = data_value[0]
        if (4 > len(initial_response)) or (0x30 < initial_response[2]):
            raise InvalidArgument()
        buffer = bytearray()
        buffer += initial_response[3:]
        data_value = data_value[1:]
        for packet in data_value:
            buffer += packet
        return bytes(buffer)
