import json
import logging

from lil.shelfio.models import Shelf, FavoriteShelf, FavoriteUser, User

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

def api_shelf_create(request):
    """create/delete favorited shelves
    """
    
    # Add shelf to user's favorite shelf
    if request.rfc5789_method in ['PUT', 'POST'] and request.user.is_authenticated():
        shelf = Shelf.objects.get(shelf_uuid=request.POST['shelf_id'])
                
        try:
            favorite_shelf = FavoriteShelf(
                user=request.user,
                shelf=shelf
            )
            favorite_shelf.save()
        except ValidationError, e:
            return HttpResponse('You have already favorited that shelf.', status=409)
                    
        return HttpResponse(status=201)

    # Remove a favorited shelf from list
    elif request.rfc5789_method == 'DELETE' and request.user.is_authenticated():
        shelf = Shelf.objects.get(shelf_uuid=request.POST['shelf_id'])
        favorite_shelf = FavoriteShelf.objects.get(shelf=shelf, user=request.user)
        favorite_shelf.delete()
        return HttpResponse(status=204)
    
    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])

def api_shelf(request, user_name):
    """Get user_name's favorite shelve"""
    
    if request.method == 'GET':
        target_user = get_object_or_404(User, username=user_name)
        
        bundled_response = _bundle_user_shelves(target_user)
        
        return HttpResponse(
            json.dumps(bundled_response, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])
    
    
def _bundle_user_shelves(target_user):
    context = {}
    
    fav_shelves = FavoriteShelf.objects.filter(user=target_user)

    shelves = []
    
    #TODO: Are we hitting the DB for each of these shelves?
    for q_shelf in fav_shelves:
        shelf_to_serialize = {
            'shelf_uuid': str(q_shelf.shelf.shelf_uuid),
            'name': q_shelf.shelf.name,
            'slug': q_shelf.shelf.slug,
            'description': q_shelf.shelf.description,
            'creation_date': q_shelf.shelf.creation_date
        }
        shelves.append(shelf_to_serialize)

    context.update({
        'user_name': target_user.username,
        'docs': shelves
    })

    return context



def api_user_create(request):
    """create/delete favorited users
    """
    
    # Add shelf to user's favorite users
    if request.rfc5789_method in ['PUT', 'POST'] and request.user.is_authenticated():
        user = User.objects.get(username=request.POST['user_name'])
                
        try:
            favorite_user = FavoriteUser(
                follower=request.user,
                leader=user
            )
            favorite_user.save()
        except ValidationError, e:
            return HttpResponse('You already have already favorited that user.', status=409)
                    
        return HttpResponse(status=201)

    # Remove a favorited user from list
    elif request.rfc5789_method == 'DELETE' and request.user.is_authenticated():
        user = User.objects.get(username=request.POST['user_name'])
        favorite_user = FavoriteUser.objects.filter(follower=request.user).filter(leader=user)
        favorite_user.delete()
        return HttpResponse(status=204)
    
    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])

def api_user(request, user_name):
    """Get user_name's favorite users"""
    
    if request.method == 'GET':
        target_user = get_object_or_404(User, username=user_name)
        
        bundled_response = _bundle_users(target_user)
        
        return HttpResponse(
            json.dumps(bundled_response, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])
    
    
def _bundle_users(target_user):
    context = {}
    
    fav_users = FavoriteUser.objects.filter(follower=target_user)

    users = []
    
    #TODO: Are we hitting the DB for each of these shelves?
    for q_user in fav_users:
        user_to_serialize = {
            'user_name': q_user.leader.username,
            'id': q_user.leader.username,
        }
        users.append(user_to_serialize)

    context.update({
        'docs': users,
        'num': len(users)
    })

    return context