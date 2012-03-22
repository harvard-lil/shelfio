from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('shlvme.views',
                          
    # API
    url(r'^api/user/(?P<url_user_name>[a-zA-Z0-9\-]*)/$', 'api_user'), # http://shlv.me/api/user/matt/
    url(r'^api/shelf/$', 'api_shelf', name='api_shelf'), # http://shlv.me/api/shelf/
    url(r'^api/shelf/(?P<url_shelf_uuid>[a-zA-Z0-9\-]+)/$', 'api_shelf', name='api_shelf'), # http://shlv.me/api/shelf/09404850-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/shelf/(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_name>[a-zA-Z0-9\-]+)/$', 'api_shelf', name='api_shelf'), # http://shlv.me/api/shelf/obama/best-novels
    url(r'^api/item/$', 'api_item', name='api_item'), # http://shlv.me/api/item
    url(r'^api/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/$', 'api_item', name='api_item'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/tag/$', 'api_tag', name='api_tag'), # http://shlv.me/api/item
    url(r'^api/tag/(?P<url_tag_uuid>[a-zA-Z0-9\-]+)/$', 'api_tag', name='api_tag'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66

    # Services
    url(r'^services/incoming/$', 'services_incoming'),    

    # Pages
    url(r'^$', 'welcome'),
    url(r'^login/$', 'process_login', name='process_login'),
    url(r'^logout/$', 'process_logout'),
    url(r'^register/$', 'process_register', name='process_register'),
    
    url(r'^(?P<user_name>[a-zA-Z0-9\-]+)/$', 'user_home'),
    url(r'^(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_name>[a-zA-Z0-9\-]+)/$', 'user_shelf'),
)
urlpatterns += staticfiles_urlpatterns()