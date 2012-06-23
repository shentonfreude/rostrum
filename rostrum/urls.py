from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.simple import direct_to_template, redirect_to
from views import home, about

admin.autodiscover()


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',                  home,           name='home'),
    url(r'^about$',             about,          name='about'),

    url(r'^app/',               include('app.urls')),

    url(r'^admin/',             include(admin.site.urls)),
)
