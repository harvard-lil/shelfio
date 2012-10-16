import json
import logging

from lil.shelfio.models import Shelf, FavoriteShelf, FavoriteUser, User, AuthTokens, Item
from lil.shelfio.views.api.v1.shelf import serialize_item

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

def api_shelves(request, user_name):
    """get all of user's favorited shelves or create a new favorite shelf
    """
    
    if request.method == 'GET': 
        # Get all of user's favorite shelves
        user = User.objects.get(username = user_name)
        
        # Build our response
        serialized_shelves = {}
        shelves = []
        
        include_private = False
        
        if not user.get_profile().favorites_are_private:
            include_private = True
        
        elif request.oauth_token:
            auth_token = AuthTokens.objects.filter(token=request.oauth_token)
            
            # Did we find that token in the DB and is it owned by the owner of the requested shelf?
            if len(auth_token) == 1 and user == auth_token.user:
                include_private = True
        
        if include_private:
            fav_shelves = FavoriteShelf.objects.filter(user=user)
                
            #TODO: Are we hitting the DB for each of these shelves?
            for fav_shelf in fav_shelves:
                shelves.append(_serialize_shelf(fav_shelf.shelf))
    
        serialized_shelves.update({
            'docs': shelves,
            'num': len(shelves)
        })
        
        return HttpResponse(json.dumps(serialized_shelves, cls=DjangoJSONEncoder), mimetype='application/json')
    
    if request.method == 'POST': 
        # Add shelf to user's favorite shelf

        shelf = get_object_or_404(Shelf, shelf_uuid=request.POST['shelf_id'])

        if request.oauth_token:
            auth_token = get_object_or_404(AuthTokens, token=request.oauth_token)
               
        try:
            favorite_shelf = FavoriteShelf(
                user=auth_token.user,
                shelf=shelf,
            )
            favorite_shelf.save()
        except ValidationError, e:
            return HttpResponse('You have already favorited that shelf.', status=409)
                    
        return HttpResponse(favorite_shelf.favorite_shelf_uuid, status=201)
    
    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])

def api_shelf(request, user_name, favorite_shelf_uuid):
    """get or delete one favorite shelf"""
    
    favorite_shelf = get_object_or_404(FavoriteShelf, favorite_shelf_uuid=favorite_shelf_uuid)
    
    include_private = False
        
    if not favorite_shelf.user.get_profile().favorites_are_private:
        include_private = True
            
    elif request.oauth_token:
        auth_token = AuthTokens.objects.filter(token=request.oauth_token)
            
        # Did we find that token in the DB and is it owned by the owner of the requested shelf?
        if len(auth_token) == 1 and favorite_shelf.user == auth_token.user:
            include_private = True
    
    if not include_private:
        return HttpResponse('Not authorized', status=401)
    
    
    if request.method == 'GET':
        # Build our response
        serialized_shelves = {}
        shelves = []
        
        shelves.append(_serialize_shelf(favorite_shelf.shelf))
    
        serialized_shelves.update({
            'docs': shelves,
            'num': len(shelves)
        })
        
        return HttpResponse(json.dumps(serialized_shelves, cls=DjangoJSONEncoder), mimetype='application/json')
            
    elif request.rfc5789_method == 'DELETE':
        # Remove a favorited shelf from list
        
        favorite_shelf.delete()
        return HttpResponse(status=204)

    else:
        return HttpResponseNotAllowed(['DELETE', 'GET'])
    
    
def _bundle_user_shelves(target_user):
    context = {}
    
    shelves = []
    
    if not target_user.get_profile().favorites_are_private:
        fav_shelves = FavoriteShelf.objects.filter(user=target_user)
        
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



def api_user(request):
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

def api_users(request, user_name):
    """Get user_name's favorite users"""
    
    if request.method == 'GET':
        target_user = get_object_or_404(User, username=user_name)
        
        bundled_response = _serialize_users(target_user)
        
        return HttpResponse(
            json.dumps(bundled_response, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])
    
def _serialize_users(target_user):
    serialized_users = {}

    users = []
    
    if not target_user.get_profile().favorites_are_private:
        fav_users = FavoriteUser.objects.filter(follower=target_user)
            
        #TODO: Are we hitting the DB for each of these shelves?
        for q_user in fav_users:
            user_to_serialize = {
                'user_name': q_user.leader.username,
                'id': q_user.leader.username,
            }
            users.append(user_to_serialize)

    serialized_users.update({
        'docs': users,
        'num': len(users)
    })

    return serialized_users

def _serialize_shelf(shelf):
    """Turn a shelf from a model object to something that can be jsonized"""
    items = Item.objects.filter(shelf=shelf)
    item_list = [serialize_item(item) for item in items]

    return {
        'shelf_uuid': str(shelf.shelf_uuid),
        'shelf_id': str(shelf.id),
        'user_name': shelf.user.username,
        'name': shelf.name,
        'description': shelf.description,
        'creation_date': shelf.creation_date,
        'is_private': shelf.is_private,
        'slug': shelf.slug,
    }