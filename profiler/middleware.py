from datetime import datetime
import inspect

import statprof

from django.db import connection
from django.core.cache import cache
from django.conf import settings


from aggregate.client import get_client

from profiler import _set_current_view, _get_current_view, _tic, _tac, _get_time, _local

class ProfilerFirstMiddleware(object):
    def process_request(self, request):
        if not hasattr(_local, 'times'):
            _local.times = {}
        _tic('req')
        _tic('mid1')

    def process_response(self, request, response):
        if True:
            _tac('mid2')
            _tac('req')
            client = get_client()
            if client is not None:
                try:
                    client.insert({'code_part': 'Middlewares Down', 'type': 'code'},
                                  {'time': _get_time('mid1'), 'count': 1})
                except StandardError:
                    pass
                try:
                    client.insert({'code_part': 'Middlewares Up', 'type': 'code'},
                                  {'time': _get_time('mid2'), 'count': 1})
                except StandardError:
                    pass
                try:
                    client.insert({'request_path': request.path, 'type': 'url'},
                                  {'time': _get_time('req'), 'count': 1})
                except StandardError:
                    pass
                try:
                    client.insert({'code_part': request.profiler_view, 'type': 'code'},
                                  {'time': _get_time('view'), 'count': 1})
                except StandardError:
                    pass
        return response


class ProfilerLastMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if inspect.ismethod(view_func):
            view_name = view_func.im_class.__module__+ '.' + view_func.im_class.__name__ + view_func.__name__
        else:
            view_name = view_func.__module__ + '.' + view_func.__name__
        
        _set_current_view(view_name)
        _tac('mid1')
        _tic('view')

    def process_response(self, request, response):
        request.profiler_view = _get_current_view()
        _set_current_view(None)
        if True:
            _tac('view')
            _tic('mid2')
        return response


class StatProfMiddleware(object):

    def process_request(self, request):
        statprof.reset(getattr(settings, 'LIVEPROFILER_STATPROF_FREQUENCY', 100))
        statprof.start()
    
    def process_response(self, request, response):
        statprof.stop()
        client = get_client()
        total_samples = statprof.state.sample_count
        if total_samples == 0:
            return response
        secs_per_sample = statprof.state.accumulated_time / total_samples

        client.insert_all([(
                    {'file' : c.key.filename,
                     'lineno' : c.key.lineno,
                     'function' : c.key.name,
                     'type' : 'python'},
                    {'self_nsamples' : c.self_sample_count,
                     'cum_nsamples' : c.cum_sample_count,
                     'tot_nsamples' : total_samples,
                     'cum_time' : c.cum_sample_count * secs_per_sample,
                     'self_time' : c.self_sample_count * secs_per_sample
                     })
                           for c in statprof.CallData.all_calls.itervalues()])



        return response
