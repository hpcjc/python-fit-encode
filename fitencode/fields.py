from struct import pack


class Field:
    field_type = 0x00
    size = 1
    pack_format = 'B'

    def __init__(self, field_def: int, size: int = 0):
        self.field_def = field_def
        self.size = size if size else self.size

    @property
    def definition(self):
        return pack('BBB', self.field_def, self.size, self.field_type)

    def pack(self, value: object) -> bytes:
        return pack(self.pack_format, self.to_fit_value(value))

    def to_fit_value(self, value: object) -> object:
        return value


class EnumField(Field):
    field_type = 0x00
    size = 1
    pack_format = 'B'


class Sint8Field(Field):
    field_type = 0x01
    size = 1
    pack_format = 'B'


class Uint8Field(Field):
    field_type = 0x02
    size = 1
    pack_format = 'B'


class Sint16Field(Field):
    field_type = 0x83
    size = 2
    pack_format = '>h'


class Uint16Field(Field):
    field_type = 0x84
    size = 2
    pack_format = '>H'


class Sint32Field(Field):
    field_type = 0x85
    size = 4
    pack_format = '>l'


class Uint32Field(Field):
    field_type = 0x86
    size = 4
    pack_format = '>L'


class Uint32zField(Field):
    field_type = 0x8C
    size = 4
    pack_format = '>L'


class StringField(Field):
    field_type = 0x07
    size = 7

    @property
    def pack_format(self) -> str:
        return f"{self.size}s"

    def to_fit_value(self, value: object) -> object:
        return str(value).encode('UTF-8')


class ByteField(Field):
    field_type = 0x0D
    size = 1

    @property
    def pack_format(self) -> str:
        return f"{self.size}s"


class FileField(EnumField):
    pass


class DateTimeField(Uint32Field):
    """seconds since UTC 00:00 Dec 31 1989"""
    pass


class LocalDateTimeField(Uint32Field):
    """seconds since 00:00 Dec 31 1989 in local time zone"""
    pass


class MessageIndexField(Uint16Field):
    pass


class EventField(EnumField):
    pass


class EventTypeField(EventField):
    pass
