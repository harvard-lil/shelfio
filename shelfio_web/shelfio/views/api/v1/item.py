import logging
import json

from lil.shelfio.models import Shelf, Item, Creator, AuthTokens

from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import F
from django.http import Http404
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

""" This is the endpoint for the item API. We CRUD the item here. Authorization only
    depends on the auth token. We don't care about the CSRF business here."""

@csrf_exempt
@require_POST
def api_item_create(request):
    """A post to the /items/ endpoint. We create a new item"""
    
    if 'shelf_uuid' in request.POST.keys() and request.POST['shelf_uuid']:
        parent_shelf = get_object_or_404(Shelf, shelf_uuid=request.POST['shelf_uuid'])
    else:
        return HttpResponse("You must supply a Shelf UUID", status=400)
        
    if not _is_authorized_to_crud_item(request, parent_shelf):
        return HttpResponse(status=404)
    
    new_item = Item(shelf=parent_shelf)
    
    new_item = _build_common_item_attributes(request, new_item)
    
    try:
        new_item.clean_fields(exclude="item_uuid")
        
    except ValidationError, e:
        return HttpResponse('There are appears to be a problem with the supplied data.', status=400)

    new_item.save()

    # Save any creators with our newly minted item id
    if 'creators' in request.POST.keys() and request.POST['creators']:
        _save_creators(request.POST['creators'], new_item)

    return HttpResponse(new_item.item_uuid, status=201)
    
@csrf_exempt
def api_item_by_uuid(request, url_item_uuid):
    """Operate on one item. The one associated with the passed-in uuid. The bulk of the item CRUD logic lives here"""
    
    if request.method == 'GET':
        try:
            item = Item.objects.get(item_uuid=url_item_uuid)
        except Item.DoesNotExist:
            return HttpResponse(status=404)
        
        parent_shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
        
        if not _is_authorized_to_read_item(request, parent_shelf):
            return HttpResponse(status=404)

        serialized_item = serialize_item(item)
        return HttpResponse(json.dumps(serialized_item, cls=DjangoJSONEncoder), mimetype='application/json')    
    
    if request.rfc5789_method == 'DELETE':
        try:
            item = Item.objects.get(item_uuid=url_item_uuid)
        except Item.DoesNotExist:
            return HttpResponse(status=404)

        parent_shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
        
        if not _is_authorized_to_crud_item(request, parent_shelf):
            return HttpResponse(status=404)

        item.delete()
        
        old_creators = Creator.objects.filter(item=item)
        
        for old_creator in old_creators:
            old_creator.delete()
            
        return HttpResponse(status=204)
    
    if request.rfc5789_method == 'PUT':
        try:
            item = Item.objects.get(item_uuid=url_item_uuid)
        except Item.DoesNotExist:
            return HttpResponse('Unable to find item_uuid', status=404)
    
        parent_shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
        
        if not _is_authorized_to_crud_item(request, parent_shelf):
            return HttpResponse(status=404)      
        
        
        # We've got a PUT, so we want to replace the old item
        new_item = Item(item_uuid=item.item_uuid, shelf=parent_shelf)
        new_item = _build_common_item_attributes(request, new_item)        
        
        try:
            new_item.clean_fields(exclude="item_uuid")    
        except ValidationError, e:
            return HttpResponse('There are appears to be a problem with the supplied data.', status=400)
    
        new_item.save()

        # TODO: clean this up. this is a super nasty hack to transfer the old item's uuid to the new item
        new_item.item_uuid = item.item_uuid
        new_item.save()

        # All should be updated. Delete the old item.
        item.delete()
    
        old_creators = Creator.objects.filter(item=item)
        
        for old_creator in old_creators:
            old_creator.delete()
            
        # If we have creators, let's save those too
        if 'creators' in request.POST.keys() and request.POST['creators']:
            _save_creators(request.POST['creators'], item)
        
        return HttpResponse(status=204)
        
    if request.rfc5789_method == 'PATCH':
        return _put_or_patch(request, url_item_uuid)

@csrf_exempt
@require_POST
def api_item_reorder(request, url_item_uuid):
    """ We allow users to drag books around in the stack to reorder them. This method
        handles the reordering details"""
        
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    if not 'sort_order' in request.POST:
        return HttpResponse(status=400)

    try:
        item = Item.objects.get(item_uuid=url_item_uuid)
    except Item.DoesNotExist:
        return HttpResponse(status=404)
    except Item.MultipleObjectsReturned:
        return HttpResponse(status=500)

    shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
    if shelf.user == request.user:
        old_so = item.sort_order
        new_so = int(request.POST['sort_order'])
        if new_so > old_so:
            Item.objects.filter(sort_order__gt=old_so).filter(sort_order__lte=new_so).update(sort_order=F('sort_order') - 1)
        else:
            Item.objects.filter(sort_order__lt=old_so).filter(sort_order__gte=new_so).update(sort_order=F('sort_order') + 1)
        item.sort_order = new_so
        item.save()
        return HttpResponse(status=200)

    return HttpResponse(status=404)

def serialize_item(item):
    """ Turn the item into something we can pass to our json encoder """
    serialized = {}
    for field in item._meta.fields:
        serialized[field.name] = getattr(item, field.name)
    serialized['item_uuid'] = str(item.item_uuid)
    serialized['shelf'] = str(item.shelf.shelf_uuid)
    creators = Creator.objects.filter(item=item)
    creators_list = [creator.name for creator in creators]
    serialized['creator'] = creators_list
    
    return serialized

def _save_creators(creators, item):
    """ Creators come in in a comma delimited string. Convert them to a list here. """
    creators = [c.strip() for c in creators.split(',')]
    for creator in creators:
        c = Creator(name=creator, item=item)
        c.save()
        
        
def _is_authorized_to_read_item(request, parent_shelf):
    """ is auth token allowed to read? That means, is not private or owned by user 
        who owns auth token """
    
    if not parent_shelf.is_private:
        return True
    
    if request.oauth_token:
        try:
            auth_token = AuthTokens.objects.get(token=request.oauth_token)
        except AuthTokens.DoesNotExist:
            raise Http404
        if auth_token.user == parent_shelf.user:
            return True
        
    return False

def _is_authorized_to_crud_item(request, parent_shelf):
    """ is auth token allowed to create, read, update delete? That meaans that the 
        item is owned by user who owns auth token """
    
    if request.oauth_token:
        try:
            auth_token = AuthTokens.objects.get(token=request.oauth_token)
        except AuthTokens.DoesNotExist:
            raise Http404
        if auth_token.user == parent_shelf.user:
            return True

    return False

def _put_or_patch(request, url_item_uuid):
    """ Our PUT and PATCH methods are identical """
    
    try:
        item = Item.objects.get(item_uuid=url_item_uuid)
    except Item.DoesNotExist:
        return HttpResponse(status=404)

    parent_shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
    
    if not _is_authorized_to_crud_item(request, parent_shelf):
        return HttpResponse(status=404)      
    
    item = _build_common_item_attributes(request, item)
    
    try:
        item.clean_fields(exclude="item_uuid")
        
    except ValidationError, e:
        return HttpResponse('There are appears to be a problem with the supplied data.', status=400)

    item.save()
    
    # If we have creators, let's save those too
    if 'creators' in request.POST.keys() and request.POST['creators']:
        _save_creators(request.POST['creators'], item)
    
    return HttpResponse(status=204)

def _build_common_item_attributes(request, item):
    """ Build item object from HTTP params. We use this for our HTTP POST, PUT, and PATCH verbs """
    
    # Shelf is not populated in this method
    # Creator is not populated in this method
    
    if 'title' in request.POST.keys() and request.POST['title']:
        item.title = request.POST['title']
    if 'link' in request.POST.keys() and request.POST['link']:
        item.link = request.POST['link']
    if 'measurement_page_numeric' in request.POST.keys() and request.POST['measurement_page_numeric']:
        item.measurement_page_numeric = request.POST['measurement_page_numeric']
    if 'measurement_height_numeric' in request.POST.keys() and request.POST['measurement_height_numeric']:
        item.measurement_height_numeric = request.POST['measurement_height_numeric']
    if 'format' in request.POST.keys() and request.POST['format']:
        item.format = request.POST['format']
    if 'shelfrank' in request.POST.keys() and request.POST['shelfrank']:
        item.shelfrank = request.POST['shelfrank']
    if 'pub_date' in request.POST.keys() and request.POST['pub_date']:
        item.pub_date = request.POST['pub_date']
    if 'isbn' in request.POST.keys():
        item.isbn = request.POST['isbn']
    if 'notes' in request.POST.keys():
        item.notes = request.POST['notes']
        
    return item