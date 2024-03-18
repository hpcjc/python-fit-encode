from struct import pack
from typing import Tuple
from fitencode import fields


MESSAGE_DATA = 0
MESSAGE_DEFINITION = 0x40


class Message:
    mesg_num = 0
    local_mesg_num = 0

    @property
    def fields(self) -> Tuple[fields.Field]:
        return tuple(
            filter(lambda t: isinstance(t[1], fields.Field),
                   self.__class__.__dict__.items()))

    @property
    def definition(self) -> bytes:
        fields_ = tuple(map(lambda kv: kv[1].definition, self.fields))
        reserved = 0
        is_big_endian = 1
        header = pack('>BBBHB',
                      MESSAGE_DEFINITION | self.local_mesg_num,
                      reserved, is_big_endian, self.mesg_num, len(fields_))
        return header + b''.join(fields_)

    def definition_override_by(self, size: dict) -> bytes:
        # Field definitions of different sizes
        fields_ = []
        for name, f in self.fields:
            if name in size:
                fields_.append(pack('BBB', f.field_def, size[name], f.field_type))
            else:
                fields_.append(f.definition)
        reserved = 0
        is_big_endian = 1
        header = pack('>BBBHB',
                      MESSAGE_DEFINITION | self.local_mesg_num,
                      reserved, is_big_endian, self.mesg_num, len(fields_))
        return header + b''.join(fields_)

    def pack(self, **kwargs) -> bytes:
        contents = list()
        for name, field in self.fields:
            if name not in kwargs.keys():
                raise Exception(f'unknown data field: {name}')
            contents.append(field.pack(kwargs[name]))
        header = pack('>B', MESSAGE_DATA | self.local_mesg_num)
        return header + b''.join(contents)


class FileId(Message):
    mesg_num = 0

    type = fields.FileField(field_def=0)
    manufacturer = fields.Uint16Field(field_def=1)
    product = fields.Uint16Field(field_def=2)
    serial_number = fields.Uint32zField(field_def=3)
    time_created = fields.DateTimeField(field_def=4)
    number = fields.Uint16Field(field_def=5)
    product_name = fields.StringField(field_def=8, size=20)


class Lap(Message):
    mesg_num = 19

    message_index = fields.MessageIndexField(field_def=254)
    timestamp = fields.DateTimeField(field_def=253)
    event = fields.EventField(field_def=0)
    event_type = fields.EventTypeField(field_def=1)
    start_time = fields.DateTimeField(field_def=2)
    start_position_lat = fields.Sint32Field(field_def=3)
    start_position_long = fields.Sint32Field(field_def=4)
    end_position_lat = fields.Sint32Field(field_def=5)
    end_position_long = fields.Sint32Field(field_def=6)
    total_elapsed_time = fields.Uint32Field(field_def=7)
    total_timer_time = fields.Uint32Field(field_def=8)
    total_distance = fields.Uint32Field(field_def=9)
    # The remaining 10 to 157 fields can be added by those who need them.


class Record(Message):
    mesg_num = 20

    timestamp = fields.DateTimeField(field_def=253)
    position_lat = fields.Sint32Field(field_def=0)
    position_long = fields.Sint32Field(field_def=1)
    altitude = fields.Uint16Field(field_def=2)
    heart_rate = fields.Uint8Field(field_def=3)
    cadence = fields.Uint8Field(field_def=4)
    distance = fields.Uint32Field(field_def=5)
    speed = fields.Uint16Field(field_def=6)
    power = fields.Uint16Field(field_def=7)
    compressed_speed_distance = fields.ByteField(field_def=8, size=3)
    grade = fields.Sint16Field(field_def=9)
    # The remaining 10 to 120 fields can be added by those who need them.


class SegmentLap(Message):
    mesg_num = 142

    message_index = fields.MessageIndexField(field_def=254)
    timestamp = fields.DateTimeField(field_def=253)
    event = fields.EventField(field_def=0)
    event_type = fields.EventTypeField(field_def=1)
    start_time = fields.DateTimeField(field_def=2)
    start_position_lat = fields.Sint32Field(field_def=3)
    start_position_long = fields.Sint32Field(field_def=4)
    end_position_lat = fields.Sint32Field(field_def=5)
    end_position_long = fields.Sint32Field(field_def=6)
    total_elapsed_time = fields.Uint32Field(field_def=7)
    total_timer_time = fields.Uint32Field(field_def=8)
    total_distance = fields.Uint32Field(field_def=9)
    # The remaining 10 to 90 fields can be added by those who need them.
    name = fields.StringField(field_def=29, size=16)


class TimestampCorrelation(Message):
    mesg_num = 162

    timestamp = fields.DateTimeField(field_def=253)
    fractional_timestamp = fields.Uint16Field(field_def=0)
    system_timestamp = fields.DateTimeField(field_def=1)
    fractional_system_timestamp = fields.Uint16Field(field_def=2)
    local_timestamp = fields.LocalDateTimeField(field_def=3)
    timestamp_ms = fields.Uint16Field(field_def=4)
    system_timestamp_ms = fields.Uint16Field(field_def=5)
