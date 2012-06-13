from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lil.shlvme.views',
                          
    # API
    url(r'^api/user/(?P<url_user_name>[a-zA-Z0-9\-]*)/$', 'user.api_user', name='api_user'), # http://shlv.me/api/user/matt/
    url(r'^api/shelf/$', 'shelf.api_shelf_create', name='api_shelf_create'), # http://shlv.me/api/shelf/
    url(r'^api/shelf/(?P<url_shelf_uuid>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_uuid', name='api_shelf_by_uuid'), # http://shlv.me/api/shelf/09404850-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/shelf/(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_name', name='api_shelf_by_name'), # http://shlv.me/api/shelf/obama/best-novels
    url(r'^api/item/$', 'item.api_item_create', name='api_item_create'), # http://shlv.me/api/item
    url(r'^api/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/$', 'item.api_item_by_uuid', name='api_item_by_uuid'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66
    url(r'^api/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/reorder/$', 'item.api_item_reorder', name='api_item_reorder'), # http://shlv.me/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66/reorder

    # Services
    url(r'^services/incoming/$', 'services.incoming', name='incoming'),    

    # Pages
    url(r'^$', 'welcome.welcome', name='welcome'),
    url(r'^about/$', 'about.about', name='about'),
    url(r'^faq/$', 'faq.faq', name='faq'),
    url(r'^add-item/$', 'item.user_create', name='user_item_create'),
    url(r'^password/change/$', auth_views.password_change, {'template_name': 'registration/password_change_form.html'}, name='auth_password_change'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logout.html'}, name='auth_logout'),
    url(r'^register/$', 'auth.process_register', name='process_register'),
    url(r'^password/change/$', auth_views.password_change, {'template_name': 'registration/password_change_form.html'}, name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/password_change_done.html'},   name='auth_password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.html'}, name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_confirm.html'}, name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name='auth_password_reset_done'),
    
    
    url(r'^(?P<user_name>[a-zA-Z0-9\-]+)/$', 'user.user_home', name='user_home'),
    url(r'^(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-_]+)/$', 'shelf.user_shelf', name='user_shelf'),
)
urlpatterns += staticfiles_urlpatterns()
