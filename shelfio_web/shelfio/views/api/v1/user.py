import json
import logging

from lil.shelfio import indexer
from lil.shelfio.models import Shelf, FavoriteUser, AuthTokens, EditProfileForm, NewShelfForm

from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.context_processors import csrf
from django.contrib.auth.models import User

from django.contrib import messages

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


@csrf_exempt
def api_user(request, url_user_name):
    """Operate on one user. usernames are unique, so we'll use them instead of a uuid. The bulk of the item CRUD logic lives here"""
    
    if request.method == 'GET':
        user = get_object_or_404(User, username=url_user_name)

        serialized_user = _serialize_user_data(request, user)
        return HttpResponse(json.dumps(serialized_user, cls=DjangoJSONEncoder), mimetype='application/json')    

    if request.rfc5789_method == 'PATCH':
        user = get_object_or_404(User, username=url_user_name)
        
        if request.oauth_token:
            auth_token = get_object_or_404(AuthTokens, token=request.oauth_token)
            if auth_token.user != user:
                raise Http404
        
        user = _build_common_attributes(request, user)

        try:
            user.clean_fields(exclude=["shelf_uuid"])
        except ValidationError, e:
            return HttpResponse('There are appears to be a problem with the supplied data.', status=400)
    
        user.save()
        
        return HttpResponse(status=204)

def _serialize_user_data(request, user):
    context = {}
    
    # We return more complete user details if owner is requesting
    is_owner = False
    
    if request.oauth_token:
        auth_token = AuthTokens.objects.get(token=request.oauth_token)
        if auth_token and auth_token.user == user:
            is_owner = True
    
    shelf_query = Shelf.objects.filter(user=user)
    shelves = []
    
    if is_owner:
        context.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'email': user.email,
        })
        shelf_query.exclude(is_private=True)

    for shelf in shelf_query:
        shelf_to_serialize = {
            'shelf_uuid': str(shelf.shelf_uuid),
            'name': shelf.name,
            'slug': shelf.slug,
            'description': shelf.description,
            'creation_date': shelf.creation_date,
            'is_private': shelf.is_private
        }
        shelves.append(shelf_to_serialize)
        
    context.update({
        'user_name': user.username,
        'docs': shelves,
    })

    return context

def _build_common_attributes(request, user):
    """ Build shelf object from HTTP params. We use this for our HTTP POST, PUT, and PATCH verbs """   
    
    if 'first_name' in request.POST.keys() and request.POST['first_name']:
        user.first_name = request.POST['first_name']
    if 'last_name' in request.POST.keys() and request.POST['last_name']:
        user.last_name = request.POST['last_name']
    if 'email' in request.POST.keys() and request.POST['email']:
        user.email = request.POST['email']
        
    return user