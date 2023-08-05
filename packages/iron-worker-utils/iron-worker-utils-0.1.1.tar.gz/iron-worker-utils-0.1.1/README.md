# iron-worker-utils

A collection of utilities for writing [IronWorker](http://www.iron.io/worker) tasks in Python.

## Functions
### get_payload

```py
>>> from iron_worker_utils import get_payload
>>> get_payload()
{u'repo': u'mwarkentin/lab', u'domain': u'http://shrinkray.io'}
```

### get_task_id

```py
>>> from iron_worker_utils import get_task_id
>>> get_task_id()
58f38c1512e3687da7be0696cbc132de29f3a1a6
```

## Installation

Add `pip "iron-worker-utils"` to your `.worker` file.

If you'd like to pin the version, use `pip "iron-worker-utils", "==0.1.1"`
