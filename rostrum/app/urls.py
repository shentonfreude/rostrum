from django.conf.urls.defaults import * #GROSS
from django.views.generic import list_detail

from models import App
#from views import acronyms, application_versions, app_details, search
#from views import report, report_current, report_development
from views import overview, details

#from views import search, browse, approved, closed
applications = {
    'queryset' : App.objects.all().order_by('acronym', 'version')
    }
# Cannot do .order_by('acronym').distinct('acronym') DISTINCT ON field in SQLite

urlpatterns = patterns(
    '',
    url(r'^$',                          overview,       name='app_overview'),
    url(r'^(?P<id>\d+)$',               details,        name='app_details'),

#    url(r'^acronym/$',            acronyms, name='acronyms'),
#    url(r'^acronym/(?P<acronym>.+)$',            acronyms, name='acronyms'),

#    url(r'^search/$',             search,             name='search'), # trailing slash needed for post to '.'

#    url(r'^report/$',             report,             name='report'),
#    url(r'^report_current/$',     report_current,     name='report_current'),
#    url(r'^report_development/$', report_development, name='report_development'),


)

