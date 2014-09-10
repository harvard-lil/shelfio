from django.conf.urls import patterns, url, include

from django.contrib import admin

admin.autodiscover()

handler404 = 'shelfio.views.simple.not_found'

urlpatterns = patterns('',
    url(r'^api/v1/', include('shelfio.urls_api')),
    url(r'^', include('shelfio.urls')),
)