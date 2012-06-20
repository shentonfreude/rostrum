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
    # Examples:
    # url(r'^$', 'rostrum.views.home', name='home'),
    # url(r'^rostrum/', include('rostrum.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$',                  home,           name='home'),
    url(r'^about$',             about,          name='about'),

#    url(r'^app/',               include('app.urls')),
#    url(r'^report/',            include('report.urls')),


    # This is a hack to make the menu bar cog link work.
    # django/contrib/admin/sites.get_urls says ^$ is 'index' -- how to use?
#    url(r'^admin$',             redirect_to, {'url': '/admin/'}, name='manage'),

    # Uncomment the next line to enable the admin:
#    url(r'^admin/',             include(admin.site.urls)),

)
