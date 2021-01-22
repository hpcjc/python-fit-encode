import io
from datetime import datetime, timedelta
from math import floor
from struct import pack


CRC_TABLE = (
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
)


class MessageType:
    DATA = 0
    DEFINITION = 0x40


class LocalMessageType:
    TIMESTAMP = 0
    RECORD = 1
    LAP = 2


class FieldDefinition:
    FID_TYPE = 0
    FID_MANUFACTURE = 1
    FID_PRODUCT = 2
    FID_SERIAL_NUMBER = 3
    TIMESTAMP = 253
    TIMESTAMP_MS = 4
    REC_TIMESTAMP = 253
    REC_HEART_RATE = 3
    REC_CADENCE = 4
    REC_SPEED = 6
    REC_POWER = 7
    LAP_TIMESTAMP = 253
    LAP_START_TIME = 2
    LAP_TOTAL_ELAPSED_TIME = 7
    LAP_TOTAL_TIMER_TIME = 8
    LAP_NAME = 29
    LAP_MESSAGE_INDEX = 254


class FieldType:
    enum = 0x00
    sint8 = 0x01
    uint8 = 0x02
    sint16 = 0x83
    uint16 = 0x84
    sint32 = 0x85
    uint32 = 0x86
    string = 0x07
    float32 = 0x88
    float64 = 0x89
    uint8z = 0x0A
    uint16z = 0x8B
    uint32z = 0x8C
    byte = 0x0D
    sint64 = 0x8E
    uint64 = 0x8F
    uint64z = 0x90


class FieldSize:
    enum = 1
    sint8 = 1
    uint8 = 1
    sint16 = 2
    uint16 = 2
    sint32 = 4
    uint32 = 4
    string = 1
    float32 = 4
    float64 = 8
    uint8z = 1
    uint16z = 2
    uint32z = 4
    byte = 1
    sint64 = 8
    uint64 = 8
    uint64z = 8


class MessageNumber:
    FILE_ID = 0
    LAP = 19
    RECORD = 20
    SEGMENT_LAP = 142
    TIMESTAMP_CORRELATION = 162


MANUFACTURE = 0x000F
PRODUCT_TYPE = 0x04
PRODUCT_ID = 0x0001
SERIAL_NUMBER = 1001


class FitMessage(object):
    message_number = 0

    def __init__(self):
        self.stream = None
        self.length = 0

    def definition(self) -> bytes:
        pass

    def data(self, **kwargs) -> bytes:
        pass

    def set_stream(self, stream: io.IOBase):
        self.stream = stream

    def append(self, **kwargs):
        if self.stream:
            self.length += self.stream.write(self.data(**kwargs))

    def definition_header(self, record_type: int, message_number: int,
                          number_of_field: int) -> bytes:
        return pack('>BBBHB',
                    record_type,
                    0,  # reserved
                    1,  # endian
                    message_number, number_of_field)


class MessageFileId(FitMessage):
    message_number = 0

    TYPE = 0
    MANUFACTURE = 1
    PRODUCT = 2
    SERIAL_NUMBER = 3

    def definition(self) -> bytes:
        field = list()
        field.append(pack('BBB',
                          self.MANUFACTURE,
                          FieldSize.uint16, FieldType.uint16))
        field.append(pack('BBB',
                          self.TYPE,
                          FieldSize.enum, FieldType.enum))
        field.append(pack('BBB',
                          self.PRODUCT,
                          FieldSize.uint16, FieldType.uint16))
        field.append(pack('BBB',
                          self.SERIAL_NUMBER,
                          FieldSize.uint32z, FieldType.uint32z))
        header = self.definition_header(
            record_type=MessageType.DEFINITION,
            message_number=self.message_number, number_of_field=len(field))
        return header + b''.join(field)

    def data(self, manufacture_id: int, product_type: int, product_id: int,
             serial_number: int) -> bytes:
        return pack('>BHBHL',
                    MessageType.DATA,
                    manufacture_id, product_type, product_id, serial_number)


class MessageTimestamp(FitMessage):
    message_number = 162

    def definition(self) -> bytes:
        field = list()
        field.append(pack('BBB',
                          FieldDefinition.TIMESTAMP,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.TIMESTAMP_MS,
                          FieldSize.uint32, FieldType.uint16))
        header = self.definition_header(
            record_type=MessageType.DEFINITION | LocalMessageType.TIMESTAMP,
            message_number=self.message_number,
            number_of_field=len(field))
        return header + b''.join(field)

    def data(self, timestamp: datetime) -> bytes:
        return pack('>BLL',
                    MessageType.DATA | LocalMessageType.TIMESTAMP,
                    floor(timestamp.timestamp()) - 631065600,
                    floor(timestamp.microsecond / 1000))


class MessageRecord(FitMessage):
    message_number = 20

    def definition(self) -> bytes:
        field = list()
        field.append(pack('BBB',
                          FieldDefinition.REC_TIMESTAMP,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.REC_HEART_RATE,
                          FieldSize.uint8, FieldType.uint8))
        field.append(pack('BBB',
                          FieldDefinition.REC_CADENCE,
                          FieldSize.uint8, FieldType.uint8))
        field.append(pack('BBB',
                          FieldDefinition.REC_SPEED,
                          FieldSize.uint16, FieldType.uint16))
        field.append(pack('BBB',
                          FieldDefinition.REC_POWER,
                          FieldSize.uint16, FieldType.uint16))
        header = self.definition_header(
            record_type=MessageType.DEFINITION | LocalMessageType.RECORD,
            message_number=self.message_number, number_of_field=len(field))
        return header + b''.join(field)

    def data(self, heart_rate: int, speed: int, cadence: int, power: int,
             timestamp: datetime) -> bytes:
        return pack('>BLBBHH',
                    MessageType.DATA | LocalMessageType.RECORD,
                    floor(timestamp.timestamp()) - 631065600,
                    heart_rate,
                    cadence,
                    speed,
                    power)


class MessageLap(FitMessage):
    message_number = 19

    def __init__(self):
        super().__init__()
        self.lap_number = 0

    def definition(self) -> bytes:
        field = list()
        field.append(pack('BBB',
                          FieldDefinition.LAP_MESSAGE_INDEX,
                          FieldSize.uint16, FieldType.uint16))
        field.append(pack('BBB',
                          FieldDefinition.LAP_TIMESTAMP,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.LAP_START_TIME,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.LAP_TOTAL_ELAPSED_TIME,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.LAP_TOTAL_TIMER_TIME,
                          FieldSize.uint32, FieldType.uint32))
        field.append(pack('BBB',
                          FieldDefinition.LAP_NAME,
                          FieldSize.string * 16, FieldType.string))
        header = self.definition_header(
            record_type=MessageType.DEFINITION | LocalMessageType.LAP,
            message_number=self.message_number, number_of_field=len(field))
        return header + b''.join(field)

    def data(self, timestamp: datetime, start_time: timedelta,
             name: str) -> bytes:
        self.lap_number += 1
        return pack('>BHLLLL16s',
                    MessageType.DATA | LocalMessageType.LAP,
                    self.lap_number,
                    floor(timestamp.timestamp()) - 631065600,
                    floor(start_time.timestamp()) - 631065600,
                    floor((timestamp - start_time).total_seconds() * 1000),
                    floor((timestamp - start_time).total_seconds() * 1000),
                    name[:16].encode('UTF-8'))


class FitEncode:
    def __init__(self, stream: io.IOBase = None):
        self.crc = 0
        self.definitions = list()
        self.length = 0

        if stream:
            self.buffer = stream
        else:
            self.buffer = io.BytesIO()

        self.buffer.write(self.fit_header())
        file_id = MessageFileId()
        self.add_definition(file_id)
        file_id.append(manufacture_id=MANUFACTURE, product_type=PRODUCT_TYPE,
                       product_id=PRODUCT_ID, serial_number=SERIAL_NUMBER)

    def fit_header(self, protocol_version: int = 0x10,
                   profile_version: int = 0x081C, data_length: int = 0):
        header_length = 14
        header = pack('<BBHL4s',
                      header_length,
                      protocol_version, profile_version, data_length,
                      '.FIT'.encode('UTF-8'))
        self.crc = 0
        return header + pack('<H', self._update_crc(header))

    def add_definition(self, message: FitMessage):
        message.set_stream(self.buffer)
        self.definitions.append(message)
        self.length += self.buffer.write(message.definition())

    def close(self):
        data_length = self.length + sum([x.length for x in self.definitions])
        header = self.fit_header(data_length=data_length)
        self.buffer.seek(0)
        self.buffer.write(header)
        self.crc = 0
        self._update_crc(self.buffer.read(-1))
        self.buffer.seek(0, 2)
        self.buffer.write(pack('H', self.crc))
        self.buffer.close()

    def _update_crc(self, data: bytes) -> int:
        for d in data:
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[int(d) & 0x0F]
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[(int(d) >> 4) & 0x0F]
        return self.crc
