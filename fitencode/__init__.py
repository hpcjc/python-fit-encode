import io
from struct import pack
from typing import Tuple
import fitencode.fields as fit_fields


CRC_TABLE = (
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
)


MESSAGE_DATA = 0
MESSAGE_DEFINITION = 0x40


class MessageBase:
    mesg_num = 0
    local_mesg_num = 0

    @property
    def fields(self) -> Tuple[fit_fields.FieldData]:
        return tuple(
            filter(lambda t: isinstance(t[1], fit_fields.FieldData),
                   self.__class__.__dict__.items()))

    @property
    def definition(self) -> bytes:
        fields = tuple(map(lambda kv: kv[1].definition, self.fields))
        reserved = 0
        is_big_endian = 1
        header = pack('>BBBHB',
                      MESSAGE_DEFINITION | self.local_mesg_num,
                      reserved, is_big_endian, self.mesg_num, len(fields))
        return header + b''.join(fields)

    def encode(self, **kwargs) -> bytes:
        contents = list()
        for name, field in self.fields:
            if name not in kwargs.keys():
                raise Exception(f'unknown data field: {name}')
            contents.append(field.encode(kwargs[name]))
        header = pack('>B', MESSAGE_DATA | self.local_mesg_num)
        return header + b''.join(contents)


class FileId(MessageBase):
    mesg_num = 0

    type = fit_fields.FileField(field_def=0)
    manufacturer = fit_fields.Uint16Field(field_def=1)
    product = fit_fields.Uint16Field(field_def=2)
    serial_number = fit_fields.Uint32zField(field_def=3)
    time_created = fit_fields.DateTimeField(field_def=4)
    number = fit_fields.Uint16Field(field_def=5)
    product_name = fit_fields.StringField(field_def=8, size=7)


class Lap(MessageBase):
    mesg_num = 19

    message_index = fit_fields.MessageIndexField(field_def=254)
    timestamp = fit_fields.DateTimeField(field_def=253)
    event = fit_fields.EventField(field_def=0)
    event_type = fit_fields.EventTypeField(field_def=1)
    start_time = fit_fields.DateTimeField(field_def=2)
    start_position_lat = fit_fields.Sint32Field(field_def=3)
    start_position_long = fit_fields.Sint32Field(field_def=4)
    end_position_lat = fit_fields.Sint32Field(field_def=5)
    end_position_long = fit_fields.Sint32Field(field_def=6)
    total_elapsed_time = fit_fields.Uint32Field(field_def=7)
    total_timer_time = fit_fields.Uint32Field(field_def=8)
    total_distance = fit_fields.Uint32Field(field_def=9)
    # The remaining 10 to 157 fields can be added by those who need them.


class Record(MessageBase):
    mesg_num = 20

    timestamp = fit_fields.DateTimeField(field_def=254)
    position_lat = fit_fields.Sint32Field(field_def=0)
    position_long = fit_fields.Sint32Field(field_def=1)
    altitude = fit_fields.Uint16Field(field_def=2)
    heart_rate = fit_fields.Uint8Field(field_def=3)
    cadence = fit_fields.Uint8Field(field_def=4)
    distance = fit_fields.Uint32Field(field_def=5)
    speed = fit_fields.Uint16Field(field_def=6)
    power = fit_fields.Uint16Field(field_def=7)
    compressed_speed_distance = fit_fields.ByteField(field_def=8, size=3)
    grade = fit_fields.Sint16Field(field_def=9)
    # The remaining 10 to 120 fields can be added by those who need them.


class TimestampCorrelation(MessageBase):
    mesg_num = 162

    timestamp = fit_fields.DateTimeField(field_def=253)
    fractional_timestamp = fit_fields.Uint16Field(field_def=0)
    system_timestamp = fit_fields.DateTimeField(field_def=1)
    fractional_system_timestamp = fit_fields.Uint16Field(field_def=2)
    local_timestamp = fit_fields.LocalDateTimeField(field_def=3)
    timestamp_ms = fit_fields.Uint16Field(field_def=4)
    system_timestamp_ms = fit_fields.Uint16Field(field_def=5)


class FitEncode:
    def __init__(self, stream: io.IOBase = None):
        self.crc = 0
        self.definitions = list()
        self.length = 0
        self.buffer = stream if stream else io.BytesIO()
        self.buffer.write(self.fit_header())

    def fit_header(self, protocol_version: int = 0x10,
                   profile_version: int = 0x081C, data_length: int = 0):
        header_length = 14
        header = pack('<BBHL4s',
                      header_length,
                      protocol_version, profile_version, data_length,
                      '.FIT'.encode('UTF-8'))
        self.crc = 0
        return header + pack('<H', self._update_crc(header))

    def add_definition(self, mesg: MessageBase):
        self.length += self.buffer.write(mesg.definition)

    def add_data(self, data: bytes):
        self.length += self.buffer.write(data)

    def finish(self):
        header = self.fit_header(data_length=self.length)
        self.buffer.seek(0)
        self.buffer.write(header)
        self.crc = 0
        self._update_crc(self.buffer.read(-1))
        self.buffer.seek(0, 2)
        self.buffer.write(pack('H', self.crc))

    def _update_crc(self, data: bytes) -> int:
        for d in data:
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[int(d) & 0x0F]
            tmp = CRC_TABLE[self.crc & 0X0F]
            self.crc = (self.crc >> 4) & 0x0FFF
            self.crc = self.crc ^ tmp ^ CRC_TABLE[(int(d) >> 4) & 0x0F]
        return self.crc
