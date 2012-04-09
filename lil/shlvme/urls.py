from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('shlvme.views',
                          
    # API
    url(r'^api/user/(?P<url_user_name>[a-zA-Z0-9\-]*)/$', 'user.api_user', name='api_user'), # http://shlv.me/api/user/matt/
    url(r'^api/shelf/$', 'shelf.api_shelf_create', name='api_shelf_create'), # http://shlv.me/api/shelf/
    url(r'^api/shelf/(?P<url_shelf_uuid>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_uuid', name='api_shelf_by_uuid'), # http://shlv.me/api/shelf/09404850-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/shelf/(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_name', name='api_shelf_by_name'), # http://shlv.me/api/shelf/obama/best-novels
    url(r'^api/item/$', 'item.api_item_create', name='api_item_create'), # http://shlv.me/api/item
    url(r'^api/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/$', 'item.api_item_by_uuid', name='api_item_by_uuid'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/reorder/$', 'item.api_item_reorder', name='api_item_reorder'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66/reorder
    url(r'^api/tag/$', 'tag.api_tag', name='api_tag'), # http://shlv.me/api/item
    url(r'^api/tag/(?P<url_tag_uuid>[a-zA-Z0-9\-]+)/$', 'tag.api_tag', name='api_tag'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66

    # Services
    url(r'^services/incoming/$', 'services.incoming', name='incoming'),    

    # Pages
    url(r'^$', 'welcome.welcome', name='welcome'),
    url(r'^login/$', 'auth.process_login', name='process_login'),
    url(r'^logout/$', 'auth.process_logout', name='process_logout'),
    url(r'^register/$', 'auth.process_register', name='process_register'),
    url(r'^add-item/$', 'item.user_create', name='user_item_create'),
    
    url(r'^(?P<user_name>[a-zA-Z0-9\-]+)/$', 'user.user_home', name='user_home'),
    url(r'^(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-_]+)/$', 'shelf.user_shelf', name='user_shelf'),
)
urlpatterns += staticfiles_urlpatterns()