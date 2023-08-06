# coding: utf-8

version_info = (0, 2, 0, 'dev', None)
__version__ = '0.2.0-dev'

import types
import logging
import time
from datetime import timedelta, datetime
import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

def every_second(seconds):
    '''
    Iterator-based timer

    @example 
    >> every(seconds=10)
    @return an iterator of timedelta object
    '''
    delta = timedelta(seconds=seconds)
    # Never return StopIteration
    while 1:
        yield delta

class every_hour(object):
    '''
    A class-based iterator that help install a timer for hourly scheduled task
    - Every hour in a day
    - Fixed hour in a day
    
    The name is chosen in all lower case to make it looks like a function because it will 
    be used as if it was a generator.
    '''
    def __init__(self, hour=None, minute=0, second=0):
        self.started = False
        self.hour = hour
        self.minute = minute
        self.second = second
    def __iter__(self):
        return self
    def next(self):
        '''
        Never return StopIteration
        '''
        if self.started is False:

            self.started = True
            now_ = datetime.now()
            if self.hour:
                # Fixed hour in a day
                # Next run will be the next day
                scheduled = now_.replace(hour=self.hour, minute=self.minute, second=self.second, microsecond=0)
                if scheduled == now_:
                    return timedelta(seconds=0)
                elif scheduled < now_:
                    # Scheduled time is passed
                    return scheduled.replace(day=now_.day + 1) - now_
            else:
                # Every hour in a day
                # Next run will be the next hour
                scheduled = now_.replace(minute=self.minute, second=self.second, microsecond=0)
                if scheduled == now_:
                    return timedelta(seconds=0)
                elif scheduled < now_:
                    # Scheduled time is passed
                    return scheduled.replace(hour=now_.hour + 1) - now_
            return scheduled - now_
        else:
            if self.hour:
                return timedelta(days=1)  # next day
            return timedelta(hours=1)  # next hour

def wait_until(time_label):
    '''
    Calculates the number of seconds that the process needs to sleep 
    '''
    if time_label == 'next_minute':
        gevent.sleep(60 - int(time.time()) % 60)
    elif time_label == 'next_hour':
        gevent.sleep(3600 - int(time.time()) % 3600)
    elif time_label == 'tomorrow':
        gevent.sleep(86400 - int(time.time()) % 86400)

class Task(object):
    '''
     A scheduled task
    '''
    def __init__(self, name, action, timer, *args, **kwargs):
        self.name = name
        self.action = action
        self.timer = timer
        self.args = args
        self.kwargs = kwargs

class Scheduler(object):
    '''
    Time-based scheduler
    '''
    def __init__(self, logger_name='greenlock.task'):
        self.logger_name = logger_name
        self.tasks = []
        self.running = True

    def schedule(self, name, timer, func, *args, **kwargs):
        '''
        ts = Scheduler('my_task')
        ts.schedule(every(seconds=10), handle_message, "Every 10 seconds")
        ts.schedule(every(seconds=30), fetch_url, url="http://yahoo.com", section="stock_ticker")
        ts.run_forever()
        '''
        self.tasks.append(Task(name, func, timer, *args, **kwargs))

    def run(self, task):
        '''
        Runs a task and re-schedule it
        '''
        if isinstance(task.timer, types.GeneratorType):
            # Starts the task immediately
            greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
            try:
                # total_seconds is available in Python 2.7
                greenlet_later = gevent.spawn_later(task.timer.next().total_seconds(), self.run, task)
                return greenlet_, greenlet_later
            except StopIteration:
                pass
            return greenlet_, None
        # Class based timer
        try:
            if task.timer.started is False:
                delay = task.timer.next().total_seconds()
                gevent.sleep(delay)
                greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
            else:
                greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
            greenlet_later = gevent.spawn_later(task.timer.next().total_seconds(), self.run, task)
            return greenlet_, greenlet_later
        except StopIteration:
            pass
        return greenlet_, None

    def run_tasks(self):
        '''
        Runs all assigned task in separate green threads. If the task should not be run, schedule it
        '''
        pool = Pool(len(self.tasks))
        for task in self.tasks:
            # Launch a green thread to schedule the task
            # A task will be managed by 2 green thread: execution thread and scheduling thread
            pool.spawn(self.run, task)
        return pool

    def run_forever(self, start_at='once'):
        """
        Starts the scheduling engine
        
        @param start_at: 'once' -> start immediately
                         'next_minute' -> start at the first second of the next minutes
                         'next_hour' -> start 00:00 (min) next hour
                         'tomorrow' -> start at 0h tomorrow
        """
        if start_at not in ('once', 'next_minute', 'next_hour', 'tomorrow'):
            raise ValueError("start_at parameter must be one of these values: 'once', 'next_minute', 'next_hour', 'tomorrow'")
        if start_at != 'once':
            wait_until(start_at)
        try:
            task_pool = self.run_tasks()
            while self.running:
                gevent.sleep(seconds=1)
            task_pool.join(timeout=30)
            task_pool.kill()
        except KeyboardInterrupt:
            # https://github.com/surfly/gevent/issues/85
            task_pool.closed = True
            task_pool.kill()
            logging.getLogger(self.logger_name).info('Time scheduler quits')

    def stop(self):
        '''
        Stops the scheduling engine
        '''
        self.running = False
