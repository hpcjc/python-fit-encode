import io
from struct import pack
import fitencode.messages


CRC_TABLE = (
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
)


class FitEncode:
    def __init__(self, buffer: io.IOBase = None):
        self.crc = 0
        self.length = 0
        self.buffer = buffer if buffer else io.BytesIO()
        self.buffer.write(self.header())

    def header(self, protocol_version: int = 0x10,
               profile_version: int = 0x081C, data_length: int = 0):
        header_length = 14
        header = pack('<BBHL4s',
                      header_length,
                      protocol_version, profile_version, data_length,
                      '.FIT'.encode('UTF-8'))
        header_crc = self._crc(0, header)
        return header + pack('<H', header_crc)

    def add_definition(self, mesg: messages.Message):
        self.add_record(mesg.definition)

    def add_record(self, record: bytes):
        self.length += self.buffer.write(record)
        self.crc = self._crc(self.crc, record)

    def finish(self):
        header = self.header(data_length=self.length)
        self.buffer.seek(0)
        self.buffer.write(header)
        self.buffer.seek(0, 2)
        self.buffer.write(pack('H', self.crc))

    @staticmethod
    def _crc(crc: int, data: bytes) -> int:
        for d in data:
            tmp = CRC_TABLE[crc & 0X0F]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ CRC_TABLE[int(d) & 0x0F]
            tmp = CRC_TABLE[crc & 0X0F]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ CRC_TABLE[(int(d) >> 4) & 0x0F]
        return crc
