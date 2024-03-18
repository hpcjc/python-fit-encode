from struct import pack
import unittest

from fitencode import FitEncode, messages, fields


class FileId(messages.FileId):
    manufacturer = messages.FileId.manufacturer
    type = messages.FileId.type
    product = messages.FileId.product
    serial_number = messages.FileId.serial_number
    product_name = messages.FileId.product_name


class ArrayUint16Field(fields.Uint16Field):
    field_type = 0x84
    pack_format = '>H'

    def pack(self, value: list) -> bytes:
        pack_format = f">{len(value)}H"
        return pack(pack_format, *value)


class AccelerometerData(messages.Message):
    mesg_num = 165
    local_mesg_num = 3

    sample_time_offset = ArrayUint16Field(field_def=1, size=2 * 30)  # unit [ms]



class ChangingListSizeTestCase(unittest.TestCase):
    def test_define_changing_list_size(self):
        fit = FitEncode()
        file_id = FileId()
        fit.add_definition(file_id)
        fit.add_record(file_id.pack(manufacturer=0x000F,
                                    type=0x04,
                                    product=0x0001,
                                    serial_number=1,
                                    product_name='TEST'))
        accel = AccelerometerData()
        fit.add_definition(accel)

        time_offset = list(range(0, 30))
        fit.add_record(accel.pack(sample_time_offset=time_offset))

        time_offset = list(range(0, 3))

        fit.add_definition(accel, size={'sample_time_offset': 2*3})
        fit.add_record(accel.pack(sample_time_offset=time_offset))

        fit.add_definition(accel)
        time_offset = list(range(30, 60))
        fit.add_record(accel.pack(sample_time_offset=time_offset))
        fit.finish()
        self.assertEqual(
            (b'\x0e\x10\x1c\x08\xcf\x00\x00\x00.FIT\x89\xff@\x00'
             b'\x01\x00\x00\x05\x01\x02\x84\x00\x01\x00\x02\x02\x84\x03\x04\x8c'
             b'\x08\x14\x07\x00\x00\x0f\x04\x00\x01\x00\x00\x00\x01TEST'
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C'
             b'\x00\x01\x00\xa5\x01\x01<\x84\x03\x00\x00\x00\x01\x00\x02\x00'
             b'\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\t\x00\n\x00'
             b'\x0b\x00\x0c\x00\r\x00\x0e\x00\x0f\x00\x10\x00\x11\x00\x12\x00'
             b'\x13\x00\x14\x00\x15\x00\x16\x00\x17\x00\x18\x00\x19\x00\x1a\x00'
             b'\x1b\x00\x1c\x00\x1dC\x00\x01\x00\xa5\x01\x01\x06\x84\x03\x00\x00'
             b'\x00\x01\x00\x02C\x00\x01\x00\xa5\x01\x01<\x84\x03\x00\x1e\x00'
             b'\x1f\x00 \x00!\x00"\x00#\x00$\x00%\x00&\x00\'\x00(\x00)\x00*\x00+'
             b'\x00,\x00-\x00.\x00/\x000\x001\x002\x003\x004\x005\x006\x007\x008'
             b'\x009\x00:\x00;b~'),
            fit.buffer.getvalue())


if __name__ == '__main__':
    unittest.main()
