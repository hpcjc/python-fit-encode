import os
import unittest
from tempfile import TemporaryDirectory

from fitencode import FitEncode, messages, fields


class FitEncodeTestCase(unittest.TestCase):
    def test_encode_header(self):
        fit = FitEncode()
        fit.finish()
        self.assertEqual(
            b'\x0e\x10\x1c\x08\x00\x00\x00\x00.FIT\xc5\xef\x00\x00',
            fit.buffer.getvalue())

    def test_file_output(self):
        with TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'test.fit')
            with open(path, 'bw') as f:
                fit = FitEncode(buffer=f)
                fit.finish()
            with open(path, 'br') as f:
                self.assertEqual(
                    b'\x0e\x10\x1c\x08\x00\x00\x00\x00.FIT\xc5\xef\x00\x00',
                    f.read(-1))

    def test_with_record(self):
        class LocalFileId(messages.FileId):
            type = messages.FileId.type
            serial_number = messages.FileId.serial_number

        fit = FitEncode()
        file_id = LocalFileId()
        fit.add_definition(file_id)
        fit.add_record(file_id.pack(type=1, serial_number=12345))
        fit.finish()
        self.assertEqual(
            (b'\x0e\x10\x1c\x08\x12\x00\x00\x00.FIT\x45\x3A\x40\x00'
             b'\x01\x00\x00\x02\x00\x01\x00\x03'
             b'\x04\x8c\x00\x01\x00\x00\x30\x39\x66\xe3'),
            fit.buffer.getvalue())


if __name__ == '__main__':
    unittest.main()
