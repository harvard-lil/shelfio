from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from lil.shlvme.models import Shelf, Item, Creator, Tag
import json
from django.contrib.auth.models import User

@csrf_exempt
def api_item(request, url_item_uuid=None):
    """API for items
    Something like shlv.me/api/item/7838a693-7ea9-4f3a-8e4f-40ad3b8492e3
    or, something like shlv.me/api/item/
    TODO: we need to validate/clean/urldecode the GET/POST values
    """
    
    # Add a new item to a shelf
    # TODO: All kinds of validation. Also, some type of transaction so that the item and creator are saved together?
    if request.method == 'POST' and request.user.is_authenticated():
        target_user = User.objects.get(username=request.user.username)
        target_shelf = Shelf.objects.get(user=target_user, name=request.POST.get('shelf-name'))

        staged_item = Item(shelf=target_shelf, title=request.POST.get('title'), isbn=request.POST.get('isbn'))
        staged_item.save()
        
        staged_creator = Creator(item=staged_item, name=request.POST.get('creator'))
        staged_creator.save()
        
        return HttpResponse(status=201)
        
    # Edit an existing shelf
    elif request.method == 'POST' and request.user.is_authenticated() and url_item_uuid is not None:
        return HttpResponse(status=202)

    # Get tags for an item
    elif request.method == 'GET' and request.user.is_authenticated() and url_item_uuid is not None:
        # Some boilerplate
        docs = []
        tags = None
        message = ''
        
        target_item = Item.objects.get(item_uuid=url_item_uuid)
        target_shelf = target_item.shelf
    
        # Get tags for item that user owns
        if request.user.is_authenticated():
            target_user = User.objects.get(username=request.user.username)
            
            # User owns the shelf
            if target_shelf.user == target_user:
                tags = Tag.objects.filter(item = target_item)
                
            else:
                tags = get_public_tags(url_item_uuid)
                
            docs = serialize_tags(tags)
           
        else:
            tags = get_public_tags(url_item_uuid)
            
            docs = serialize_tags(tags)
        

        object_to_serialize = {}

        object_to_serialize['item_uuid'] = str(target_shelf.shelf_uuid)
        object_to_serialize['num_found'] = len(docs)
        object_to_serialize['docs'] = docs
        object_to_serialize['message'] = message

        return HttpResponse(json.dumps(object_to_serialize, cls=DjangoJSONEncoder), mimetype='application/json')
        