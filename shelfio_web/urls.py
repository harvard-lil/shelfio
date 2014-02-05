from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

handler404 = 'lil.shelfio.views.simple.not_found'

urlpatterns = patterns('',
    url(r'^api/v1/', include('lil.shelfio.urls_api')),
    url(r'^', include('lil.shelfio.urls')),
)