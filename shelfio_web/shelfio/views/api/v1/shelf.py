import logging
import json

from shelfio.models import Shelf, Item, Creator, AuthTokens
from shelfio.views.api.v1.item import serialize_item

from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import F
from django.http import Http404
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

""" This is the endpoint for the shelf API. We CRUD the item here. Authorization only
    depends on the auth token. We don't care about the CSRF business here."""

@csrf_exempt
@require_POST
def api_shelf_create(request):
    """A post to the /shelf/ endpoint. We create a new shelf"""
        
    if request.oauth_token:
        auth_token = get_object_or_404(AuthTokens, token=request.oauth_token)
    
    new_shelf = Shelf(user=auth_token.user)
    new_shelf = _build_common_attributes(request, new_shelf)
    
    try:
        new_shelf.clean_fields(exclude=["shelf_uuid", "slug"])
        
    except ValidationError, e:
        return HttpResponse('There appears to be a problem with the supplied data.', status=400)

    new_shelf.save()

    return HttpResponse(new_shelf.shelf_uuid, status=201)


@csrf_exempt
def api_shelf_by_uuid(request, url_shelf_uuid):
    """Operate on one shelf. The one associated with the passed-in uuid. The bulk of the item CRUD logic lives here"""
    
    if request.method == 'GET':
        shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)
                
        if not _is_authorized_to_read(request, shelf):
            return HttpResponse(status=404)

        serialized_shelf = serialize_shelf(shelf)
        return HttpResponse(json.dumps(serialized_shelf, cls=DjangoJSONEncoder), mimetype='application/json')

    if request.rfc5789_method == 'DELETE':
        shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)

        if not _is_authorized_to_crud(request, shelf):
            return HttpResponse(status=404)

        shelf.delete()
            
        return HttpResponse(status=204)
    
    if request.rfc5789_method == 'PUT':
        shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)
        
        if not _is_authorized_to_crud(request, shelf):
            return HttpResponse(status=404)      
        
        # We've got a PUT, so we want to replace the old shelf
        new_shelf = Shelf(user=shelf.user)
        new_shelf = _build_common_attributes(request, new_shelf)
        
        try:
            new_shelf.clean_fields(exclude=["shelf_uuid", "slug"])    
        except ValidationError, e:
            return HttpResponse('There are appears to be a problem with the supplied data.', status=400)
    
        new_shelf.save()

        # TODO: clean this up. this is a super nasty hack to transfer the old shelf's uuid to the new item
        new_shelf.shelf_uuid = shelf.shelf_uuid
        new_shelf.save()

        # All should be updated. Delete the old item.
        shelf.delete()
                
        return HttpResponse(status=204)
    
    if request.rfc5789_method == 'PATCH':
        shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)
        
        if not _is_authorized_to_crud(request, shelf):
            return HttpResponse(status=404)   

        try:
            shelf.clean_fields(exclude=["shelf_uuid", "slug"])
            
        except ValidationError, e:
            return HttpResponse('There are appears to be a problem with the supplied data.', status=400)
    
        shelf = _build_common_attributes(request, shelf)
    
        shelf.save()
        
        return HttpResponse(status=204)

  
def _is_authorized_to_read(request, shelf):
    """ is auth token allowed to read? That means, is not private or owned by user 
        who owns auth token """
    
    if not shelf.is_private:
        return True
    
    # Do we have a token in the request?
    if request.oauth_token:
        auth_token = AuthTokens.objects.filter(token=request.oauth_token)
        # Did we find that token in the DB and is it owned by the owner of the requested shelf?
        if len(auth_token) == 1 and auth_token.user == shelf.user:
            return True
                
    return False

def _is_authorized_to_crud(request, shelf):
    """ is auth token allowed to create, read, update delete? That means that the 
        item is owned by user who owns auth token """
    
    if request.oauth_token:
        auth_token = AuthTokens.objects.get(token=request.oauth_token)
        if auth_token and auth_token.user == shelf.user:
            return True

    return False

def _build_common_attributes(request, shelf):
    """ Build shelf object from HTTP params. We use this for our HTTP POST, PUT, and PATCH verbs """   
    
    if 'name' in request.POST.keys() and request.POST['name']:
        shelf.name = request.POST['name']
    if 'description' in request.POST.keys() and request.POST['description']:
        shelf.description = request.POST['description']
    if 'is_private' in request.POST.keys() and request.POST['is_private']:
        shelf.is_private = request.POST['is_private']
        
    return shelf

def serialize_shelf(shelf):
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
        'docs': item_list,
        'start': -1,
        'num_found': len(item_list)
    }