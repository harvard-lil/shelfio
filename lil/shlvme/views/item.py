from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from lil.shlvme.models import Shelf, Item, Creator, Tag, AddItemForm
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.context_processors import csrf

@csrf_exempt
def api_item_create(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    if request.method == 'POST':
        pass

    return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def api_item_by_uuid(request, url_item_uuid):
    pass

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

def user_create(request):
    if not request.user.is_authenticated():
        messages.warning(request, 'You need to sign in to add items.')
        return redirect(reverse('process_login'))
    
    context = {}
    context.update(csrf(request))

    if request.method == 'GET':
        add_item_form = AddItemForm(request.user, initial=request.GET)

    elif request.method == 'POST':
        add_item_form = AddItemForm(request.user, request.POST)
        if add_item_form.is_valid():
            add_item_form.save()
            return redirect(reverse(
                'user_shelf',
                args=[request.user.username, add_item_form.cleaned_data['shelf'].slug],
            ))

    context.update({
        'user': request.user,
        'add_item_form': add_item_form
    })
    return render_to_response('item/create.html', context)