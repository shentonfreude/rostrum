from django.conf.urls.defaults import * #GROSS
from django.views.generic import list_detail

from models import Application
from views import acronyms, application_versions, app_details, search
from views import report, report_current, report_development

#from views import search, browse, approved, closed
applications = {
    'queryset' : Application.objects.all().order_by('acronym', 'release')
    }
# Cannot do .order_by('acronym').distinct('acronym') DISTINCT ON field in SQLite

urlpatterns = patterns(
    '',
    url(r'^$',               application_versions, name='app_versions'),

    url(r'^acronym/$',            acronyms, name='acronyms'),
    url(r'^acronym/(?P<acronym>.+)$',            acronyms, name='acronyms'),

    url(r'^search/$',             search,             name='search'), # trailing slash needed for post to '.'

    url(r'^report/$',             report,             name='report'),
    url(r'^report_current/$',     report_current,     name='report_current'),
    url(r'^report_development/$', report_development, name='report_development'),

    url(r'^(?P<object_id>\d+)$',       app_details, name='app_details'),

    # url(r'^(?P<object_id>\d+)$',  list_app_versions, name="list_app_versions"),
    # url(r'^version/(?P<object_id>\d+)$',  version_details, name="version_details"),
    # url(r'^csvimport$',        csvimport, name="csvimport"),
#    url(r'^$',                     browse, name="projects"),
#    url(r'^approved$',             approved, name="approved"),
#    url(r'^closed$',               closed, name="closed"),
#    url(r'^search/$',              search, name="search"),
#    url(r'^new/$',                 create_object, {'model': Application}), # For admins only
)

