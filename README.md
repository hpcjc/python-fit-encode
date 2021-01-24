# Python library for ANT/Garmin .FIT file encode

This library provides a primitive interface for encoding __Flexible and Interoperable
Data Transfer (FIT) Protocol__ and a high-level interface for message definition.

## USAGE

```
from fitencode import FitEncode, fields, messages
from datetime import datetime
from math import floor


"""
Define a subset of messages to be used (local messages)
"""
class LocalFileId(messages.FileId):
    """ Subset of the global FileId"""
    manufacturer = fields.Uint16Field(field_def=1)
    type = fields.FileField(field_def=0)
    product = fields.Uint16Field(field_def=2)
    serial_number = fields.Uint32zField(field_def=3)


class LocalRecord(messages.Record):
    """Subset of the global Record"""
    local_mesg_num = 1

    timestamp = fields.DateTimeField(field_def=253)
    heart_rate = fields.Uint8Field(field_def=3)
    cadence = fields.Uint8Field(field_def=4)
    speed = fields.Uint16Field(field_def=6)
    power = fields.Uint16Field(field_def=7)


with open('file.fit', 'bw') as f:
    fit = FitEncode(stream=f)
    file_id = LocalFileId()
    fit.add_definition(file_id)
    fit.add_record(
        file_id.pack(manufacturer=0x000F,
                     type=0x04,
                     product=0x0001,
                     serial_number=1001))

    record = LocalRecord()
    fit.add_definition(record)
    fit.add_record(
        record.pack(heart_rate=120, cadence=85,
                    speed=floor((45/3.6) * 1000), power=311,
                    timestamp=floor(datetime(2021, 1, 2, 12, 15, 0).timestamp() - 631065600))
    fit.add_record(
        record.pack(heart_rate=121, cadence=88,
                    speed=floor((45.2/3.6) * 1000), power=330,
                    timestamp=floor(datetime(2021, 1, 2, 12, 15, 1).timestamp() - 631065600))
    fit.finish()
```

## INSTALL

```
pip install git+https://github.com/hpcjc/python-fit-encode
```

## EXAMPLE

Create an _Activity_ that contains _Time correlation_, _Record_ and _Lap_ messages.

```
from fitencode import FitEncode, messages, fields
from datetime import datetime
from math import floor


class LocalFileId(messages.FileId):
    manufacturer = messages.FileId.manufacture
    type = messages.FileId.type
    product = messages.FileId.product
    serial_number = messages.FileId.serial_number


class LocalTimestampCorrelation(messages.TimestampCorrelation):
    local_mesg_num = 0
    timestamp = messages.TimestampCorrelation.timestamp
    timestamp_ms = fields.Uint32Field(field_def=4)


class LocalRecord(messages.Record):
    local_mesg_num = 1
    timestamp = messages.Record.timestamp
    heart_rate = messages.Record.heart_rate
    cadence = messages.Record.cadence
    speed = messages.Record.speed
    power = messages.Record.power


class LocalLap(messages.Lap):
    local_mesg_num = 2
    message_index = messages.Lap.message_index
    timestamp = messages.Lap.timestamp
    start_time = messages.Lap.start_time
    total_elapsed_time = messages.Lap.total_elapsed_time
    total_timer_time = messages.Lap.total_timer_time
    name = messages.Lap.name


with open('activity.fit', 'bw') as f:
    fit = FitEncode(stream=f)
    file_id = LocalFileId()
    fit.add_definition(file_id)
    fit.add_record(
        file_id.encode(manufacturer=0x000F,
                       type=0x04,
                       product=0x0001,
                       serial_number=1001))

    # Add the definition of the local message to be used
    timestamp = LocalTimestampCorrelation()
    record = LocalRecord()
    lap = LocalLap()
    fit.add_definition(timestamp)
    fit.add_definition(record)
    fit.add_definition(lap)

    # Adding a 'Lap 1' data records
    fit.add_record(timestamp.encode(timestamp=1,timestamp_ms=2))
    fit.add_record(
        record.encode(timestamp=1,heart_rate=156, cadence=89,
                      speed=floor((45/3.6) * 1000), power=353))
    fit.add_record(timestamp.encode(timestamp=2,timestamp_ms=210))
    fit.add_record(
        record.encode(timestamp=2,heart_rate=157, cadence=90,
                      speed=floor((45.5/3.6) * 1000), power=354))
    fit.add_record(timestamp.encode(timestamp=3,timestamp_ms=220))
    fit.add_record(
        record.encode(timestamp=3,heart_rate=158, cadence=91,
                      speed=floor((45.8/3.6) * 1000), power=353))
    fit.add_record(
        lap.encode(message_index=0,
                   timestamp=3, start_time=1,
                   total_elapsed_time=2, total_timer_time=2, name="Lap 1"))

    # Adding a 'Lap 2' data records.
    fit.add_record(timestamp.encode(timestamp=4,timestamp_ms=2))
    fit.add_record(
        record.encode(timestamp=4, heart_rate=156, cadence=89,
                      speed=floor((45/3.6) * 1000), power=353))
    fit.add_record(timestamp.encode(timestamp=5,timestamp_ms=210))
    fit.add_record(
        record.encode(timestamp=5,heart_rate=157, cadence=90,
                      speed=floor((45.5/3.6) * 1000), power=354))
    fit.add_record(timestamp.encode(timestamp=6,timestamp_ms=220))
    fit.add_record(
        record.encode(timestamp=6,heart_rate=158, cadence=91,
                      speed=floor((45.8/3.6) * 1000), power=353))
    fit.add_record(
        lap.encode(message_index=1,
                   timestamp=6, start_time=3,
                   total_elapsed_time=3, total_timer_time=3, name="Lap 2"))
    fit.finish()
```
