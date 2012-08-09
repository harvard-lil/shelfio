from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

handler404 = 'lil.shelfio.views.commons.not_found'

urlpatterns = patterns('',
    url(r'^', include('lil.shelfio.urls'))
)