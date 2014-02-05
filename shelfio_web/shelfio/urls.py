from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('shelfio.views',

    # Common Pages
    url(r'^$', 'welcome.welcome', name='welcome'),
    url(r'^about/$', 'simple.about', name='about'),
    url(r'^faq/$', 'simple.faq', name='faq'),
    url(r'^search/$', 'simple.search', name='search'),
    url(r'^privacy/$', 'simple.privacy', name='privacy'),
    url(r'^bookmark/$', 'simple.bookmark', name='bookmark'),
    
    # Session/account management
    url(r'^password/change/$', auth_views.password_change, {'template_name': 'registration/password_change_form.html'}, name='auth_password_change'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logout.html'}, name='auth_logout'),
    url(r'^register/$', 'user_management.process_register', name='process_register'),
    url(r'^password/change/$', auth_views.password_change, {'template_name': 'registration/password_change_form.html'}, name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/password_change_done.html'},   name='auth_password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.html'}, name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_confirm.html'}, name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name='auth_password_reset_done'),

    # Add item page
    url(r'^add-item/$', 'item.user_create', name='user_item_create'), # user can create new shelf on item page
    
    # User page
    url(r'^(?P<user_name>[a-zA-Z0-9\-]+)/$', 'user.user_home', name='user_home'),
    url(r'^(?P<user_name>[a-zA-Z0-9\-]+)/helpers/$', 'user.helpers', name='user_helpers'),
    
    #  Shelf page
    url(r'^(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-_]+)/$', 'shelf.user_shelf', name='user_shelf'),
    url(r'^(?P<url_user_name>[a-zA-Z0-9\-]+)/embed/(?P<url_shelf_slug>[a-zA-Z0-9\-_]+)/$', 'shelf.embed_shelf', name='embed_shelf'),
    
)
urlpatterns += staticfiles_urlpatterns()