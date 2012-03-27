from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from lil.shlvme.models import Shelf, Item, Creator
import json
from django.contrib.auth.models import User

@csrf_exempt
def api_shelf(request, url_shelf_uuid=None, url_user_name=None, url_shelf_name=None):
    """API for shelves
    Something like shlv.me/api/shelf/5138a693-7ea9-4f3a-8e4f-40ad3b847ef9
    Or, something like shlv.me/api/shelf/
    TODO: we need to validate/clean/urldecode the GET/POST values
    """
    # Create a new shelf
    if request.method == 'POST' and request.user.is_authenticated():
        target_user = User.objects.get(username=request.user.username)
        shelf = Shelf(user=target_user, name=request.POST.get('shelf-name'), description=request.POST.get('description'), is_public=request.POST.get('is-public'))
        shelf.save()
        
        return HttpResponse(status=201)
        
    # Edit an existing shelf
    elif request.method == 'POST' and request.user.is_authenticated() and url_shelf_uuid is not None:
        return HttpResponse(status=202)
    
    # Delete an existing shelf
    elif request.method == 'DELETE' and request.user.is_authenticated() and url_shelf_uuid is not None:
        target_user = User.objects.get(username=request.user.username)
        shelf = Shelf.objects.get(user=target_user, shelf_uuid=url_shelf_uuid)
        shelf.delete()
        
        return HttpResponse(status=202)
    
    # Get one shelf from a shelf_uuid
    elif request.method == 'GET' and url_shelf_uuid is not None:
        # Some boilerplate
        docs = []
        shelves = None
        message = ''
    
        if request.user.is_authenticated():
            target_user = User.objects.get(username=request.user.username)
            shelves = Shelf.objects.filter(user=target_user).filter(shelf_uuid=url_shelf_uuid)

            docs = _serialize_shelves_with_items(shelves)
        else:
            shelves = Shelf.objects.filter(is_public=True).filter(shelf_uuid=url_shelf_uuid)

            docs = _serialize_shelves_with_items(shelves)

        object_to_serialize = {}
    
        # TODO: start and limit are placeholders at this point
        object_to_serialize['limit'] = 0
        object_to_serialize['start'] = 0
        object_to_serialize['num_found'] = len(docs)
        object_to_serialize['docs'] = docs
        object_to_serialize['message'] = message

        return HttpResponse(json.dumps(object_to_serialize, cls=DjangoJSONEncoder), mimetype='application/json')
    
    # Get one shelf from a user name and a shelf name
    elif request.method == 'GET' and url_user_name is not None and url_shelf_name is not None:
        # Some boilerplate
        docs = []
        shelves = None
        message = ''
    
        if request.user.is_authenticated() and request.user.username == url_user_name:
            target_user = User.objects.get(username=request.user.username)
            shelves = Shelf.objects.filter(user=target_user).filter(name=url_shelf_name)
            
            docs = _serialize_shelves_with_items(shelves)
           
        else:
            target_user = User.objects.get(username=url_user_name)
            shelves = Shelf.objects.filter(user=target_user).filter(name=url_shelf_name).filter(is_public=True)
            
            docs = _serialize_shelves_with_items(shelves)
        
        object_to_serialize = {}
    
        # TODO: start and limit are placeholders at this point
        object_to_serialize['shelf_uuid'] = str(shelves[0].shelf_uuid)
        object_to_serialize['user_name'] = shelves[0].user.username
        object_to_serialize['name'] = shelves[0].name
        object_to_serialize['description'] = shelves[0].description
        object_to_serialize['creation_date'] = shelves[0].creation_date
        object_to_serialize['is_public'] = shelves[0].is_public
        object_to_serialize['limit'] = 0
        object_to_serialize['start'] = 0
        object_to_serialize['num_found'] = len(docs)
        object_to_serialize['docs'] = docs
        object_to_serialize['message'] = message

        return HttpResponse(json.dumps(object_to_serialize, cls=DjangoJSONEncoder), mimetype='application/json')

def user_shelf(request, url_user_name, url_shelf_slug):
    """A user's shelf."""
    target_user = get_object_or_404(User, username=url_user_name)
    target_shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)

    if request.method == 'GET':
        if target_shelf.is_public or target_user == request.user:
            return render_to_response('shelf/show.html', {
                'user': request.user,
                'shelf_user': target_user,
                'is_owner': request.user == target_user,
                'shelf': target_shelf
            })
        else:
            raise Http404

    # POSTS, PATCHES, DELETES, still to come
    else:
        pass

def _serialize_shelves_with_items(shelves):
    docs = []

    for shelf in shelves:
        doc = {}
        doc['shelf_uuid'] = str(shelf.shelf_uuid)
        doc['user_name'] = shelf.user.username
        doc['name'] = shelf.name
        doc['description'] = shelf.description
        doc['creation_date'] = shelf.creation_date
        doc['is_public'] = shelf.is_public
        
        list_of_items = []
        item_to_serialize = {}
        items = Item.objects.filter(shelf=shelves)
        for item in items:
            target_creators = Creator.objects.filter(item=item)
            creators_list = []
            for target_creator in target_creators:
                creators_list.append(target_creator.name)
            
            doc['item_uuid'] = str(item.item_uuid)
            doc['title'] = item.title
            doc['creator'] = creators_list
            doc['isbn'] = item.isbn                   
            doc['web_location'] = item.link
            doc['measurement_height_numeric'] = float(item.measurement_height_numeric)
            doc['measurement_page_numeric'] = item.measurement_page_numeric
            doc['pub_date'] = item.pub_date
            doc['shelfrank'] = item.shelfrank
            doc['content_type'] = item.content_type
            doc['creation_date'] = item.creation_date
            doc['sort_order'] = item.sort_order    
            
            list_of_items.append(item_to_serialize)                   
            
        doc['items'] = list_of_items
        docs.append(doc)
        
    return docs