import json
import logging

from shelfio.models import Shelf, FavoriteShelf
from shelfio.views.api.v1 import shelf as api

from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.context_processors import csrf
from django.contrib.sites.models import Site
from django.conf import settings


logger = logging.getLogger(__name__)

def user_shelf(request, url_user_name, url_shelf_slug):
    """A user's shelf."""
    target_user = get_object_or_404(User, username=url_user_name)
    target_shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)
    shelf_name = target_shelf.name
    api_response = api.api_shelf(request, target_shelf)
    
    if request.user.is_authenticated():
        referer_fallback = reverse('user_home', args=[request.user.username])
    else:
        referer_fallback = reverse('welcome')
    referer = request.META.get(
        'HTTP_REFERER',
        referer_fallback,
    )

    if api_response.status_code == 204:
        messages.info(request, shelf_name + ' has been deleted.')
        return redirect(referer)
    elif api_response.status_code == 404:
        raise Http404
    elif api_response.status_code >= 400:
        messages.error(request, api_response.content)
        return redirect(referer)

    shelf = json.loads(api_response.content)
    
    favorite_shelf_flag = False
    
    if request.user.is_authenticated():
        favorite_shelf = FavoriteShelf.objects.filter(shelf=target_shelf).filter(user=request.user)
        favorite_shelf_flag = len(favorite_shelf) == 1
        
    context = {
        'user': request.user,
        'shelf_user': target_user,
        'is_owner': request.user == target_user,
        'is_favorite': favorite_shelf_flag,
        'shelf_uuid': shelf['shelf_uuid'],
        'shelf_items': json.dumps(shelf['docs'], cls=DjangoJSONEncoder),
        'shelf_name': shelf_name,
        'shelf_slug': shelf['slug'],
        'shelf_domain' : Site.objects.get_current().domain,
        'shelf_description': shelf['description'],
        'SHELFIO_API_LOCATION': SHELFIO_API['LOCATION'],
    }
    context.update(csrf(request))

    if request.rfc5789_method in ['POST', 'PATCH', 'PUT'] and api_response.status_code == 200:
        messages.success(request, shelf_name + ' has been saved.')
        return redirect(referer)

    context.update({ 'messages': messages.get_messages(request) })
    return render_to_response('shelf/show.html', context)
    
def embed_shelf(request, url_user_name, url_shelf_slug):
    """An embeddable shelf."""
    target_user = get_object_or_404(User, username=url_user_name)
    target_shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)
    shelf_name = target_shelf.name
    api_response = api.api_shelf(request, target_shelf)

    shelf = json.loads(api_response.content)
    context = {
        'shelf_user': target_user,
        'shelf_items': json.dumps(shelf['docs'], cls=DjangoJSONEncoder),
        'shelf_name': shelf_name,
        'shelf_slug': shelf['slug'],
    }

    return render_to_response('shelf/embed.html', context)