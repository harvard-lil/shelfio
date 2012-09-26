from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('lil.shelfio.views.api',

    # Auth API
    url(r'^authorizations/$', 'authorizations.api_tokens', name='api_tokens'), # http://shelf.io/api/v1/authorizations/
    url(r'^authorizations/(?P<token>[a-zA-Z0-9\-]+)/$', 'authorizations.api_one_token', name='api_one_token'), # http://shelf.io/api/v1/authorizations/7daace3a-0734-11e2-9946-c42c033233c6/

)
urlpatterns += staticfiles_urlpatterns()