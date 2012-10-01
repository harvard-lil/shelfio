from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('lil.shelfio.views.api.v1',

    # Authorizations
    url(r'^authorizations/$', 'authorizations.api_tokens', name='api_tokens'), # http://shelf.io/api/v1/authorizations/
    url(r'^authorizations/(?P<token>[a-zA-Z0-9\-]+)/$', 'authorizations.api_one_token', name='api_one_token'), # http://shelf.io/api/v1/authorizations/7daace3a-0734-11e2-9946-c42c033233c6/
    
    # Favorites
    url(r'^favorites/user/$', 'favorites.api_user_create', name='api_favorite_user_create'), # http://shelf.io/api/favorite/user/
    url(r'^favorites/user/(?P<user_name>[a-zA-Z0-9\-]+)/$', 'favorites.api_user', name='api_favorite_user'), # http://shelf.io/api/favorite/user/
    url(r'^favorites/shelf/$', 'favorites.api_shelf_create', name='api_favorite_shelf_create'), # http://shelf.io/api/favorite/shelf/
    url(r'^favorites/shelf/(?P<user_name>[a-zA-Z0-9\-]+)/$', 'favorites.api_shelf', name='api_favorite_shelf'), # http://shelf.io/api/favorite/shelf/obama/

    # Search
    url(r'^search/(?P<target_type>[a-zA-Z0-9\-]+)/$', 'search.api_search', name='api_search'), # http://shelf.io/api/search/
    
    # Misc
    url(r'^shelfroulette/$', 'roulette.api_shelf', name='api_shelfroulette'), # http://shelf.io/api/search/
)
urlpatterns += staticfiles_urlpatterns()