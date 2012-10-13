from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('lil.shelfio.views.api.v1',

    # Search
    url(r'^(?P<target_type>[item|user]+)/search/$', 'search.api_search', name='api_search'), # http://shelf.io/api/search/

    # Items
    url(r'^item/$', 'item.api_item_create', name='api_item_create'), # http://shelf.io/api/item
    url(r'^item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/$', 'item.api_item_by_uuid', name='api_item_by_uuid'), # http://shelf.io/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66
    
    # Shelves
    url(r'^shelf/$', 'shelf.api_shelf_create', name='api_shelf_create'), # http://shelf.io/api/shelf/
    url(r'^shelf/(?P<url_shelf_uuid>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_uuid', name='api_shelf_by_uuid'), # http://shelf.io/api/shelf/09404850-6c65-11e1-b0c4-0800200c9a66
    #url(r'^shelf/(?P<url_user_name>[a-zA-Z0-9\-]+)/(?P<url_shelf_slug>[a-zA-Z0-9\-]+)/$', 'shelf.api_shelf_by_name', name='api_shelf_by_name'), # http://shelf.io/api/shelf/obama/best-novels

    # API
    url(r'^user/(?P<url_user_name>[a-zA-Z0-9\-]*)/$', 'user.api_user', name='api_user'), # http://shelf.io/api/user/matt/

    # Authorizations
    url(r'^authorizations/$', 'authorizations.api_tokens', name='api_tokens'), # http://shelf.io/api/v1/authorizations/
    url(r'^authorizations/(?P<token>[a-zA-Z0-9\-]+)/$', 'authorizations.api_one_token', name='api_one_token'), # http://shelf.io/api/v1/authorizations/7daace3a-0734-11e2-9946-c42c033233c6/
    
    # Favorites
    url(r'^favorites/user/$', 'favorites.api_user_create', name='api_favorite_user_create'), # http://shelf.io/api/favorite/user/
    url(r'^favorites/user/(?P<user_name>[a-zA-Z0-9\-]+)/$', 'favorites.api_user', name='api_favorite_user'), # http://shelf.io/api/favorite/user/
    url(r'^favorites/shelf/$', 'favorites.api_shelf_create', name='api_favorite_shelf_create'), # http://shelf.io/api/favorite/shelf/
    url(r'^favorites/shelf/(?P<user_name>[a-zA-Z0-9\-]+)/$', 'favorites.api_shelf', name='api_favorite_shelf'), # http://shelf.io/api/favorite/shelf/obama/

    # Misc services (these are more of "do something over/with the data" than "CRUD the data")
    url(r'^services/incoming/$', 'services.incoming', name='incoming'),
    url(r'^services/export/(?P<shelf_uuid>[a-zA-Z0-9\-]+)/$', 'export.export_shelf_as_csv', name='export_shelf'),   
    url(r'^services/shelfroulette/$', 'roulette.api_shelf', name='api_shelfroulette'), # http://shelf.io/api/search/
    url(r'^services/reorder/item/(?P<url_item_uuid>[a-zA-Z0-9\-]+)/$', 'item.api_item_reorder', name='api_item_reorder'), # http://shelf.io/api/shelf/30bc5090-6c65-11e1-b0c4-0800200c9a66/reorder
    #put search here (?)
)
urlpatterns += staticfiles_urlpatterns()