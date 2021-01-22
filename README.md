# Python library for ANT/Garmin .FIT file encode


## USAGE

```
from fitencode import FitEncode, MessageRecord
from datetime import datetime
from math import floor

with open('new.fit', 'bw+') as f:
    fit = FitEncode(stream=f)
    record = MessageRecord()
    fit.add_definition(record)

    record.append(heart_rate=120, cadence=85,
                  speed=floor((45/3.6) * 1000),
                  power=311,
                  timestamp=datetime(2021, 1, 2, 12, 15, 0))
    record.append(heart_rate=122, cadence=90,
                  speed=floor((46/3.6) * 1000),
                  power=310,
                  timestamp=datetime(2021, 1, 2, 12, 15, 1))
    fit.close()
```

## INSTALL

```
pip install git+https://github.com/hpcjc/python-fit-encode
```
