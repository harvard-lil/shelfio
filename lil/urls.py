from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

handler404 = 'lil.shlvme.views.commons.not_found'

urlpatterns = patterns('',
    url(r'^shlvme/', include('lil.shlvme.urls'))
)