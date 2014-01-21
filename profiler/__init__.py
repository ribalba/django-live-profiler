from datetime import datetime
import threading

_local = threading.local()
_local.times = {}

def _set_current_view(view):
    _local.current_view = view

def _get_current_view():
    return getattr(_local, 'current_view', None)

def _tic(key):
    _local.times[key] = datetime.now()

def _tac(key):
    try:
        _local.times[key] = datetime.now() - _local.times[key]
        return _local.times[key]
    except KeyError:
        pass

def _get_time(key):
    t = _local.times[key]
    return t.seconds + float(t.microseconds) / 10**6
