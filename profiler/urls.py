from django.conf.urls.defaults import *

urlpatterns = patterns(
    'profiler.views',
    url(r'^$', 'global_stats', name='profiler_global_stats'),
    url(r'^by_view/$', 'stats_by_view', name='profiler_stats_by_view'),
    url(r'^code/$', 'python_stats', name='profiler_python_stats'),
    url(r'^views/$', 'views_stats', name='profiler_views_stats'),
    url(r'^urls/$', 'urls_stats', name='profiler_urls_stats'),
    url(r'^reset/$', 'reset', name='profiler_reset'),
    )

