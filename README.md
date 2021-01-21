# Python library for ANT/Garmin .FIT file serializer


## USAGE

```
from fitserialize import Serializer

with open('path/to/log.fit', 'bw+') as f:
    fit = Serializer(stream=f)
    fit.append(...)
    fit.close()
```

## INSTALL

```
pip install git+https://github.com/hpcjc/python-fit-serialize
```
