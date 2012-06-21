from django.conf.urls.defaults import * #GROSS
from django.views.generic import list_detail

from models import App
from views import overview, details, administrative, compliance

urlpatterns = patterns(
    '',
    url(r'^$',                          overview,       name='app_overview'),
    url(r'^(?P<id>\d+)$',               details,        name='app_details'),
    url(r'^administrative/$',           administrative, name='app_administrative'),
    url(r'^compliance/$',               compliance,     name='app_compliance'),

#    url(r'^search/$',             search,             name='search'), # trailing slash needed for post to '.'

#    url(r'^report/$',             report,             name='report'),
#    url(r'^report_current/$',     report_current,     name='report_current'),
#    url(r'^report_development/$', report_development, name='report_development'),


)

