# Python library for ANT/Garmin .FIT file encode


## USAGE

```
from fitencode import FitEncode, FileId, Record
from datetime import datetime
from math import floor


class LocalFileId(FileId):
    manufacturer = fields.Uint16Field(field_def=1)
    type = fields.FileField(field_def=0)
    product = fields.Uint16Field(field_def=2)
    serial_number = fields.Uint32zField(field_def=3)


class LocalRecord(Record):
    local_mesg_num = 1

    timestamp = fields.DateTimeField(field_def=253)
    heart_rate = fields.Uint8Field(field_def=3)
    cadence = fields.Uint8Field(field_def=4)
    speed = fields.Uint16Field(field_def=6)
    power = fields.Uint16Field(field_def=7)


with open('new.fit', 'bw+') as f:
    fit = FitEncode(stream=f)
    file_id = LocalFileId()
    fit.add_definition(file_id)
    fit.add_data(
        file_id.encode(manufacturer=0x000F, type=0x04, product=0x0001, serial_number=1001))

    record = LocalRecord()
    fit.add_definition(record)

    fit.add_data(
        record.encode(heart_rate=120, cadence=85,
                      speed=floor((45/3.6) * 1000), power=311,
                      timestamp=floor(datetime(2021, 1, 2, 12, 15, 0).timestamp() - 631065600))
    fit.add_data(
        record.encode(heart_rate=121, cadence=88,
                      speed=floor((45.2/3.6) * 1000), power=330,
                      timestamp=floor(datetime(2021, 1, 2, 12, 15, 1).timestamp() - 631065600))
    fit.finish()
```

## INSTALL

```
pip install git+https://github.com/hpcjc/python-fit-encode
```

## EXAMPLE

```
from fitencode import FitEncode, FileId, TimestampCorrelation, Record, Lap
from fitencode import fields
from datetime import datetime
from math import floor


class LocalFileId(FileId):
    manufacturer = fields.Uint16Field(field_def=1)
    type = fields.FileField(field_def=0)  # FIXME: 銭湯に移動する必要がある
    product = fields.Uint16Field(field_def=2)
    serial_number = fields.Uint32zField(field_def=3)


class LocalTimestampCorrelation(TimestampCorrelation):
    local_mesg_num = 0
    timestamp = fields.DateTimeField(field_def=253)
    timestamp_ms = fields.Uint32Field(field_def=4)


class LocalRecord(Record):
    local_mesg_num = 1
    timestamp = fields.DateTimeField(field_def=253)
    heart_rate = fields.Uint8Field(field_def=3)
    cadence = fields.Uint8Field(field_def=4)
    speed = fields.Uint16Field(field_def=6)
    power = fields.Uint16Field(field_def=7)


class LocalLap(Lap):
    local_mesg_num = 2
    message_index = fields.MessageIndexField(field_def=254)
    timestamp = fields.DateTimeField(field_def=253)
    start_time = fields.DateTimeField(field_def=2)
    total_elapsed_time = fields.Uint32Field(field_def=7)
    total_timer_time = fields.Uint32Field(field_def=8)
    name = fields.StringField(field_def=29, size=16)


with open('new.fit', 'bw+') as f:
    fit = FitEncode(stream=f)
    file_id = LocalFileId()
    fit.add_definition(file_id)
    fit.add_data(file_id.encode(manufacturer=0x000F, type=0x04, product=0x0001, serial_number=1001))

    timestamp = LocalTimestampCorrelation()
    record = LocalRecord()
    lap = LocalLap()
    fit.add_definition(timestamp)
    fit.add_definition(record)
    fit.add_definition(lap)

    # Lap 1
    fit.add_data(timestamp.encode(timestamp=1,timestamp_ms=2))
    fit.add_data(record.encode(
        timestamp=1,heart_rate=156, cadence=89, speed=floor((45/3.6) * 1000), power=353))
    fit.add_data(timestamp.encode(timestamp=2,timestamp_ms=210))
    fit.add_data(record.encode(
        timestamp=2,heart_rate=157, cadence=90, speed=floor((45.5/3.6) * 1000), power=354))
    fit.add_data(timestamp.encode(timestamp=3,timestamp_ms=220))
    fit.add_data(record.encode(
        timestamp=3,heart_rate=158, cadence=91, speed=floor((45.8/3.6) * 1000), power=353))
    fit.add_data(lap.encode(message_index=0, timestamp=3, start_time=1, total_elapsed_time=2, total_timer_time=2, name="Lap 1"))
    # Lap 2
    fit.add_data(timestamp.encode(timestamp=4,timestamp_ms=2))
    fit.add_data(record.encode(
        timestamp=4,heart_rate=156, cadence=89, speed=floor((45/3.6) * 1000), power=353))
    fit.add_data(timestamp.encode(timestamp=5,timestamp_ms=210))
    fit.add_data(record.encode(
        timestamp=5,heart_rate=157, cadence=90, speed=floor((45.5/3.6) * 1000), power=354))
    fit.add_data(timestamp.encode(timestamp=6,timestamp_ms=220))
    fit.add_data(record.encode(
        timestamp=6,heart_rate=158, cadence=91, speed=floor((45.8/3.6) * 1000), power=353))
    fit.add_data(lap.encode(message_index=1, timestamp=6, start_time=3, total_elapsed_time=3, total_timer_time=3, name="Lap 2"))
    fit.finish()
```
