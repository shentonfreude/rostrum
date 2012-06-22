from django.conf.urls.defaults import * #GROSS
from django.views.generic import list_detail

from models import App
from views import overview, details, uploadcsv
from views import administrative, compliance, description, technical

urlpatterns = patterns(
    '',
    url(r'^$',                          overview,       name='app_overview'),
    url(r'^(?P<id>\d+)$',               details,        name='app_details'),
    url(r'^uploadcsv/$',                uploadcsv,      name='app_uploadcsv'),
    url(r'^administrative/$',           administrative, name='app_administrative'),
    url(r'^compliance/$',               compliance,     name='app_compliance'),
    url(r'^description/$',              description,    name='app_description'),
    url(r'^technical/$',                technical,      name='app_technical'),

#    url(r'^search/$',             search,             name='search'), # trailing slash needed for post to '.'
)

