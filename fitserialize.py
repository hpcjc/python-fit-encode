import io
from datetime import datetime
from math import floor
from struct import pack


CRC_TABLE = (
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
)
MESSAGE_NUM_FILE_ID = 0
MESSAGE_NUM_TIMESTAMP_CORRELATION = 162
MESSAGE_NUM_RECORD = 20
DEFINITION_MESSAGE = 0x40
DATA_MESSAGE = 0

FILE_ID_MANUFACTURE = 0x000F
FILE_ID_TYPE = 0x04
FILE_ID_PRODUCT = 0x0001
FILE_ID_SERIAL_NUMBER = 1001

FIELD_DEFINITION_NUM_FID_TYPE = 0
FIELD_DEFINITION_NUM_FID_MANUFACTURE = 1
FIELD_DEFINITION_NUM_FID_PRODUCT = 2
FIELD_DEFINITION_NUM_FID_SERIAL_NUMBER = 3
FIELD_DEFINITION_NUM_TIMESTAMP = 253
FIELD_DEFINITION_NUM_TIMESTAMP_MS = 4
FIELD_DEFINITION_NUM_REC_TIMESTAMP = 253
FIELD_DEFINITION_NUM_REC_HEART_RATE = 3
FIELD_DEFINITION_NUM_REC_CADENCE = 4
FIELD_DEFINITION_NUM_REC_SPEED = 6
FIELD_DEFINITION_NUM_REC_POWER = 7

JCF_LOCAL_MSG_TYPE_TIMESTAMP = 0
JCF_LOCAL_MSG_TYPE_RECORD = 1

DM_BASE_TYPE_enum = 0x00
DM_BASE_TYPE_sint8 = 0x01
DM_BASE_TYPE_uint8 = 0x02
DM_BASE_TYPE_sint16 = 0x83
DM_BASE_TYPE_uint16 = 0x84
DM_BASE_TYPE_sint32 = 0x85
DM_BASE_TYPE_uint32 = 0x86
DM_BASE_TYPE_string = 0x07
DM_BASE_TYPE_float32 = 0x88
DM_BASE_TYPE_float64 = 0x89
DM_BASE_TYPE_uint8z = 0x0A
DM_BASE_TYPE_uint16z = 0x8B
DM_BASE_TYPE_uint32z = 0x8C
DM_BASE_TYPE_byte = 0x0D
DM_BASE_TYPE_sint64 = 0x8E
DM_BASE_TYPE_uint64 = 0x8F
DM_BASE_TYPE_uint64z = 0x90


class Serializer:
    def __init__(self, stream: io.IOBase = None):
        self.is_initialized = False
        self.crc = 0
        self.data_length = 0

        if stream:
            self.buffer = stream
        else:
            self.buffer = io.BytesIO()
        self.buffer.write(self.create_fit_header())
        size = self.buffer.write(self.create_definition_file_id())
        size += self.buffer.write(self.create_file_id())
        size += self.buffer.write(self.create_definition_timestamp())
        size += self.buffer.write(self.create_definition_record())
        self.data_length = size

    def create_fit_header(self, data_length: int = 0):
        msg = dict(size=14, protocol_version=0x10,
                   profile_version=0x081C,
                   data_length=data_length, crc=0)
        header = pack('<BBHL4s',
                      msg['size'], msg['protocol_version'],
                      msg['profile_version'], msg['data_length'],
                      '.FIT'.encode('UTF-8'))
        self.crc = 0
        return header + pack('<H', self.update_crc(header))

    def create_definition_header(self, record_type: int, message_number: int,
                                 number_of_field: int) -> bytes:
        return pack('>BBBHB',
                    record_type,
                    0,  # reserved
                    1,  # endian
                    message_number, number_of_field)

    def create_definition_file_id(self) -> bytes:
        content = list()
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_FID_MANUFACTURE,
                            2, DM_BASE_TYPE_uint16))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_FID_TYPE,
                            1, DM_BASE_TYPE_enum))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_FID_PRODUCT,
                            2, DM_BASE_TYPE_uint16))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_FID_SERIAL_NUMBER,
                            4, DM_BASE_TYPE_uint32z))
        header = self.create_definition_header(
            record_type=DEFINITION_MESSAGE,
            message_number=MESSAGE_NUM_FILE_ID, number_of_field=len(content))
        return header + b''.join(content)

    def create_definition_timestamp(self) -> bytes:
        content = list()
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_TIMESTAMP,
                            4, DM_BASE_TYPE_uint32))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_TIMESTAMP_MS,
                            4, DM_BASE_TYPE_uint16))  # TODO: ここはuint32?
        header = self.create_definition_header(
            record_type=DEFINITION_MESSAGE | JCF_LOCAL_MSG_TYPE_TIMESTAMP,
            message_number=MESSAGE_NUM_TIMESTAMP_CORRELATION,
            number_of_field=len(content))
        return header + b''.join(content)

    def create_definition_record(self) -> bytes:
        content = list()
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_REC_TIMESTAMP,
                            4, DM_BASE_TYPE_uint32))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_REC_HEART_RATE,
                            1, DM_BASE_TYPE_uint8))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_REC_CADENCE,
                            1, DM_BASE_TYPE_uint8))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_REC_SPEED,
                            2, DM_BASE_TYPE_uint16))
        content.append(pack('BBB',
                            FIELD_DEFINITION_NUM_REC_POWER,
                            2, DM_BASE_TYPE_uint16))
        header = self.create_definition_header(
            record_type=DEFINITION_MESSAGE | JCF_LOCAL_MSG_TYPE_RECORD,
            message_number=MESSAGE_NUM_RECORD,
            number_of_field=len(content))
        return header + b''.join(content)

    def create_file_id(self) -> bytes:
        return pack('>BHBHL',
                    DATA_MESSAGE, FILE_ID_MANUFACTURE, FILE_ID_TYPE,
                    FILE_ID_PRODUCT, FILE_ID_SERIAL_NUMBER)

    def create_timestamp_data(self, timestamp: datetime) -> bytes:
        return pack('>BLL',
                    DATA_MESSAGE | JCF_LOCAL_MSG_TYPE_TIMESTAMP,
                    floor(timestamp.timestamp()) - 631065600,
                    floor(timestamp.microsecond / 1000))\

    def create_record_data(self, heart_rate: int, speed: int,
                           cadence: int, power: int,
                           timestamp: datetime) -> bytes:
        return pack('>BLBBHH',
                    DATA_MESSAGE | JCF_LOCAL_MSG_TYPE_RECORD,
                    floor(timestamp.timestamp()) - 631065600,
                    heart_rate,
                    cadence,
                    speed,
                    power)

    def append(self, heart_rate: int, speed: int, cadence: int, power: int,
               timestamp: datetime):
        data_length = 0
        data_length += self.buffer.write(
            self.create_timestamp_data(timestamp))
        data_length += self.buffer.write(
            self.create_record_data(
                heart_rate, speed, cadence, power, timestamp))
        self.data_length += data_length

    def close(self):
        header = self.create_fit_header(data_length=self.data_length)
        self.buffer.seek(0)
        self.buffer.write(header)
        self.crc = 0
        self.update_crc(self.buffer.read(-1))
        self.buffer.seek(0, 2)
        self.buffer.write(pack('H', self.crc))
        self.buffer.close()

    def update_crc(self, data: bytes) -> int:
        for d in data:
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[int(d) & 0x0F]
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[(int(d) >> 4) & 0x0F]
        return self.crc
