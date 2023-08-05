import datetime
import os
import pickle
import re
import sys
import threading
import time
import uuid
from functools import wraps

from huey.exceptions import DataStoreGetException
from huey.exceptions import DataStorePutException
from huey.exceptions import DataStoreTimeout
from huey.exceptions import QueueException
from huey.exceptions import QueueReadException
from huey.exceptions import QueueRemoveException
from huey.exceptions import QueueWriteException
from huey.registry import registry
from huey.utils import EmptyData
from huey.utils import local_to_utc
from huey.utils import wrap_exception


class Huey(object):
    """
    Huey executes tasks by exposing function decorators that cause the function
    call to be enqueued for execution by the consumer.

    Typically your application will only need one Huey instance, but you can
    have as many as you like -- the only caveat is that one consumer process
    must be executed for each Huey instance.

    :param queue: a queue instance, e.g. ``RedisQueue()``
    :param result_store: a place to store results and the task schedule,
        e.g. ``RedisResultStore()``
    :param store_none: Flag to indicate whether tasks that return ``None``
        should store their results in the result store.
    :param always_eager: Useful for testing, this will execute all tasks
        immediately, without enqueueing them.

    Example usage::

        from huey.api import Huey, crontab
        from huey.backends.redis_backend import RedisQueue, RedisDataStore

        queue = RedisQueue('my-app')
        result_store = RedisDataStore('my-app')
        huey = Huey(queue, result_store)

        @huey.task()
        def slow_function(some_arg):
            # ... do something ...
            return some_arg

        @huey.periodic_task(crontab(minute='0', hour='3'))
        def backup():
            # do a backup every day at 3am
            return
    """
    def __init__(self, queue, result_store=None, store_none=False,
                 always_eager=False, schedule_key='schedule'):
        self.queue = queue
        self.result_store = result_store
        self.blocking = self.queue.blocking
        self.store_none = store_none
        self.always_eager = always_eager
        self.schedule_key = schedule_key
        self._schedule = {}
        self._lock = threading.Lock()

    def task(self, retries=0, retry_delay=0, retries_as_argument=False):
        def decorator(func):
            """
            Decorator to execute a function out-of-band via the consumer.
            """
            klass = create_task(QueueTask, func, retries_as_argument)

            def schedule(args=None, kwargs=None, eta=None, delay=None,
                         convert_utc=True):
                if delay and eta:
                    raise ValueError('Both a delay and an eta cannot be '
                                     'specified at the same time')
                if delay:
                    eta = (datetime.datetime.now() +
                           datetime.timedelta(seconds=delay))
                if convert_utc and eta:
                    eta = local_to_utc(eta)
                cmd = klass(
                    (args or (), kwargs or {}),
                    execute_time=eta,
                    retries=retries)
                return self.enqueue(cmd)

            func.schedule = schedule
            func.task_class = klass

            @wraps(func)
            def inner_run(*args, **kwargs):
                cmd = klass(
                    (args, kwargs),
                    retries=retries,
                    retry_delay=retry_delay)
                return self.enqueue(cmd)
            return inner_run
        return decorator

    def periodic_task(self, validate_datetime):
        """
        Decorator to execute a function on a specific schedule.
        """
        def decorator(func):
            def method_validate(self, dt):
                return validate_datetime(dt)

            klass = create_task(
                PeriodicQueueTask,
                func,
                validate_datetime=method_validate
            )

            func.task_class = klass

            def _revoke(revoke_until=None, revoke_once=False):
                self.revoke(klass(), revoke_until, revoke_once)
            func.revoke = _revoke

            def _is_revoked(dt=None, peek=True):
                return self.is_revoked(klass(), dt, peek)
            func.is_revoked = _is_revoked

            def _restore():
                return self.restore(klass())
            func.restore = _restore

            return func
        return decorator

    def _wrapped_operation(exc_class):
        def decorator(fn):
            def inner(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except:
                    wrap_exception(exc_class)
            return inner
        return decorator

    @_wrapped_operation(QueueWriteException)
    def _write(self, msg):
        self.queue.write(msg)

    @_wrapped_operation(QueueReadException)
    def _read(self):
        return self.queue.read()

    @_wrapped_operation(QueueRemoveException)
    def _remove(self, msg):
        return self.queue.remove(msg)

    @_wrapped_operation(DataStoreGetException)
    def _get(self, key, peek=False):
        if peek:
            return self.result_store.peek(key)
        else:
            return self.result_store.get(key)

    @_wrapped_operation(DataStorePutException)
    def _put(self, key, value):
        return self.result_store.put(key, value)

    def enqueue(self, task):
        if self.always_eager:
            return task.execute()

        self._write(registry.get_message_for_task(task))

        if self.result_store:
            return AsyncData(self, task)

    def dequeue(self):
        message = self._read()
        if message:
            return registry.get_task_for_message(message)

    def execute(self, task):
        if not isinstance(task, QueueTask):
            raise TypeError('Unknown object: %s' % task)

        result = task.execute()

        if result is None and not self.store_none:
            return

        if self.result_store and not isinstance(task, PeriodicQueueTask):
            self._put(task.task_id, pickle.dumps(result))

        return result

    def revoke(self, task, revoke_until=None, revoke_once=False):
        if not self.result_store:
            raise QueueException('A DataStore is required to revoke task')

        serialized = pickle.dumps((revoke_until, revoke_once))
        self._put(task.revoke_id, serialized)

    def restore(self, task):
        self._get(task.revoke_id)  # simply get and delete if there

    def is_revoked(self, task, dt=None, peek=True):
        if not self.result_store:
            return False
        res = self._get(task.revoke_id, peek=True)
        if res is EmptyData:
            return False
        revoke_until, revoke_once = pickle.loads(res)
        if revoke_once:
            # This task *was* revoked for one run, but now it should be
            # restored to normal execution.
            if not peek:
                self.restore(task)
            return True
        return revoke_until is None or revoke_until > dt

    def flush(self):
        self.queue.flush()

    def load_schedule(self):
        if not self.result_store:
            return
        with self._lock:
            serialized = self.result_store.get(self.schedule_key)
            if not serialized or serialized is EmptyData:
                return

            for task_string in pickle.loads(serialized):
                try:
                    task_obj = registry.get_task_for_message(task_string)
                    self.add_schedule(task_obj)
                except QueueException:
                    pass

    def save_schedule(self):
        if not self.result_store:
            return
        with self._lock:
            serialized_tasks = pickle.dumps([
                registry.get_message_for_task(c) for c in self.schedule()])
            self.result_store.put(self.schedule_key, serialized_tasks)

    def ready_to_run(self, cmd, dt=None):
        dt = dt or datetime.datetime.now()
        return cmd.execute_time is None or cmd.execute_time <= dt

    def add_schedule(self, cmd):
        if not self.is_pending(cmd):
            self._schedule[cmd.task_id] = cmd

    def remove_schedule(self, cmd):
        if self.is_pending(cmd):
            del(self._schedule[cmd.task_id])

    def is_pending(self, cmd):
        return cmd.task_id in self._schedule

    def schedule(self):
        return self._schedule.values()


class AsyncData(object):
    def __init__(self, huey, task):
        self.huey = huey
        self.task = task

        self._result = EmptyData

    def _get(self):
        task_id = self.task.task_id
        if self._result is EmptyData:
            res = self.huey._get(task_id)

            if res is not EmptyData:
                self._result = pickle.loads(res)
                return self._result
            else:
                return res
        else:
            return self._result

    def get(self, blocking=False, timeout=None, backoff=1.15, max_delay=1.0,
            revoke_on_timeout=False):
        if not blocking:
            res = self._get()
            if res is not EmptyData:
                return res
        else:
            start = time.time()
            delay = .1
            while self._result is EmptyData:
                if timeout and time.time() - start >= timeout:
                    if revoke_on_timeout:
                        self.revoke()
                    raise DataStoreTimeout
                if delay > max_delay:
                    delay = max_delay
                if self._get() is EmptyData:
                    time.sleep(delay)
                    delay *= backoff

            return self._result

    def revoke(self):
        self.huey.revoke(self.task)

    def restore(self):
        self.huey.restore(self.task)


class QueueTaskMetaClass(type):
    def __init__(cls, name, bases, attrs):
        """
        Metaclass to ensure that all task classes are registered
        """
        registry.register(cls)


class QueueTask(object):
    """
    A class that encapsulates the logic necessary to 'do something' given some
    arbitrary data.  When enqueued with the :class:`Huey`, it will be
    stored in a queue for out-of-band execution via the consumer.  See also
    the :meth:`task` decorator, which can be used to automatically
    execute any function out-of-band.

    Example::

    class SendEmailTask(QueueTask):
        def execute(self):
            data = self.get_data()
            send_email(data['recipient'], data['subject'], data['body'])

    huey.enqueue(
        SendEmailTask({
            'recipient': 'somebody@spam.com',
            'subject': 'look at this awesome website',
            'body': 'http://youtube.com'
        })
    )
    """

    __metaclass__ = QueueTaskMetaClass

    def __init__(self, data=None, task_id=None, execute_time=None, retries=0,
                 retry_delay=0):
        self.set_data(data)
        self.task_id = task_id or self.create_id()
        self.revoke_id = 'r:%s' % self.task_id
        self.execute_time = execute_time
        self.retries = retries
        self.retry_delay = retry_delay

    def create_id(self):
        return str(uuid.uuid4())

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def execute(self):
        """Execute any arbitary code here"""
        raise NotImplementedError

    def __eq__(self, rhs):
        return (
            self.task_id == rhs.task_id and
            self.execute_time == rhs.execute_time and
            type(self) == type(rhs))


class PeriodicQueueTask(QueueTask):
    def create_id(self):
        return registry.task_to_string(type(self))

    def validate_datetime(self, dt):
        """Validate that the task should execute at the given datetime"""
        return False


def create_task(task_class, func, retries_as_argument=False, **kwargs):
    def execute(self):
        args, kwargs = self.data or ((), {})
        if retries_as_argument:
            kwargs['retries'] = self.retries
        return func(*args, **kwargs)

    attrs = {
        'execute': execute,
        '__module__': func.__module__,
        '__doc__': func.__doc__
    }
    attrs.update(kwargs)

    klass = type(
        'queuecmd_%s' % (func.__name__),
        (task_class,),
        attrs
    )

    return klass

dash_re = re.compile('(\d+)-(\d+)')
every_re = re.compile('\*\/(\d+)')

def crontab(month='*', day='*', day_of_week='*', hour='*', minute='*'):
    """
    Convert a "crontab"-style set of parameters into a test function that will
    return True when the given datetime matches the parameters set forth in
    the crontab.

    Acceptable inputs:
    * = every distinct value
    */n = run every "n" times, i.e. hours='*/4' == 0, 4, 8, 12, 16, 20
    m-n = run every time m..n
    m,n = run on m and n
    """
    validation = (
        ('m', month, range(1, 13)),
        ('d', day, range(1, 32)),
        ('w', day_of_week, range(7)),
        ('H', hour, range(24)),
        ('M', minute, range(60))
    )
    cron_settings = []
    min_interval = None

    for (date_str, value, acceptable) in validation:
        settings = set([])

        if isinstance(value, int):
            value = str(value)

        for piece in value.split(','):
            if piece == '*':
                settings.update(acceptable)
                continue

            if piece.isdigit():
                piece = int(piece)
                if piece not in acceptable:
                    raise ValueError('%d is not a valid input' % piece)
                settings.add(piece)

            else:
                dash_match = dash_re.match(piece)
                if dash_match:
                    lhs, rhs = map(int, dash_match.groups())
                    if lhs not in acceptable or rhs not in acceptable:
                        raise ValueError('%s is not a valid input' % piece)
                    settings.update(range(lhs, rhs+1))
                    continue

                every_match = every_re.match(piece)
                if every_match:
                    interval = int(every_match.groups()[0])
                    settings.update(acceptable[::interval])

        cron_settings.append(sorted(list(settings)))

    def validate_date(dt):
        _, m, d, H, M, _, w, _, _ = dt.timetuple()

        # fix the weekday to be sunday=0
        w = (w + 1) % 7

        for (date_piece, selection) in zip([m, d, w, H, M], cron_settings):
            if date_piece not in selection:
                return False

        return True

    return validate_date
