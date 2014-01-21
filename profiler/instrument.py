from datetime import datetime
from functools import partial

from django.conf import settings
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.constants import MULTI
from django.db import connection

from aggregate.client import get_client

from profiler import _get_current_view

def instrumented_execute(self, *args, **kwargs):
    start = datetime.now()
    try:
        return self._real_execute(*args, **kwargs)
    finally:
        client = get_client()
        d = (datetime.now() - start)
        client.insert({'query' : args[0], 'view' : _get_current_view(),
                       'type' : 'sql'},
                      {'time' : 0.0 + d.seconds * 1000 + \
                       float(d.microseconds)/1000, 'count' : 1})

def instrumented_cursor(self, *args, **kwargs):
    cursor = self.__class__.cursor(self, *args, **kwargs)
    cursor._real_execute = cursor.execute
    cursor.execute = partial(instrumented_execute, cursor)
    return cursor

def instrumented_init(self, *args, **kwargs):
    args[1].cursor = partial(instrumented_cursor, args[1])
    self._real_init(*args, **kwargs)

INSTRUMENTED = False

if not INSTRUMENTED and getattr(settings, 'LIVE_PROFILER_SQL_INSTRUMENT',
                                True):
    SQLCompiler._real_init = SQLCompiler.__init__
    SQLCompiler.__init__ = instrumented_init
    INSTRUMENTED = True
