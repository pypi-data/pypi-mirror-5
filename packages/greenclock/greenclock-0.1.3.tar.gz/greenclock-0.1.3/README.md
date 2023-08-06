GreenClock
==========

GreenClock is a time-based task scheduler using gevent

With GreenClock, you can: Schedule a task to run every X seconds, daily, weekly, monthly, 
or at certain times (such as application startup).

GreenClock launches a green thread per task. Therefore every task will be executed in a concurrent manner,
without blocking each other.

### Status

This module is currently under development.

### Installation

To install GreenClock from [pip](https://pypi.python.org/pypi/pip):

```bash
    $ pip install greenclock
```


To install GreenClock from source:
```bash
    $ git clone git@github.com:pcdinh/greenclock.git
    $ python setup.py install
```

### Usage

```

import greenclock
from datetime import datetime
import time

def func_1():
    print('Calling func_1() at ' + str(datetime.now()))
    time.sleep(2)
    print('Ended call to func_1() at ' + str(datetime.now()))

def func_2():
    print('Calling func_2() at ' + str(datetime.now()))
    time.sleep(2)
    print('Ended call to func_2() at ' + str(datetime.now()))

if __name__ == "__main__":
    scheduler = greenclock.Scheduler(logger_name='task_scheduler')
    scheduler.schedule('task_1', func_1, greenclock.every(seconds=4))
    scheduler.schedule('task_2', func_2, greenclock.every(seconds=1))
    # to start the scheduled tasks immediately, specify 'once' for `start_at`
    # other values: 
    # * `next_minute`: Wait to the first seconds of the next minute to run
    # * `next_hour`: Wait to the first seconds of the next hour to run
    # * `tomorrow`: Wait to the first seconds of tomorrow to run
    scheduler.run_forever(start_at='once')

```
