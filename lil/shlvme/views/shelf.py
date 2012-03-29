from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from lil.shlvme.models import Shelf, Item, Creator, NewShelfForm, AddItemForm
import json
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.context_processors import csrf

@csrf_exempt
def api_shelf_create(request):
    if request.method == 'POST' and request.user.is_authenticated():
        form = NewShelfForm(request.POST)
        if form.is_valid():
            shelf = Shelf(
                user=request.user,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                is_public=form.cleaned_data['is_public'],
            )
            shelf.save()
        else:
            return HttpResponse(400)
        return HttpResponse(status=201)

    # POST but not authenticated
    elif request.method == 'POST':
        return HttpResponse(status=401)

    # Method not supported
    else:
        return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def api_shelf_by_uuid(request, url_shelf_uuid):
    # /shlv.me/api/shelf/5138a693-7ea9-4f3a-8e4f-40ad3b847ef9
    shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)
    return api_shelf(request, shelf)

@csrf_exempt
def api_shelf_by_name(request, url_user_name, url_shelf_slug):
    # /shlv.me/api/shelf/some-username/some-shelf-slug
    target_user = get_object_or_404(User, username=url_user_name)
    shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)

    return api_shelf(request, shelf)

def api_shelf(request, shelf):
    if request.user != shelf.user and not shelf.is_public:
        return HttpResponse(status=404)

    # Edit shelf
    elif request.method in ('PATCH', 'PUT') and request.user.is_authenticated():
        try:
            serialized = _serialize_shelf(_update_shelf_data(shelf, request.POST))
        except ValidationError, e:
            return HttpResponse(status=400)
        return HttpResponse(
            json.dumps(serialized, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    # Delete shelf
    elif request.method == 'DELETE' and request.user.is_authenticated():
        shelf.delete()
        return HttpResponse(status=204)

    # Create Item, add to shelf
    elif request.method == 'POST' and request.user.is_authenticated:
        pass

    elif request.method == 'GET':
        serialized_shelf = _serialize_shelf(shelf)
        return HttpResponse(
            json.dumps(serialized_shelf, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    else:
        return HttpResponseNotAllowed(['POST', 'PATCH', 'PUT', 'DELETE', 'GET'])

def user_shelf(request, url_user_name, url_shelf_slug):
    """A user's shelf."""
    target_user = get_object_or_404(User, username=url_user_name)
    target_shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)
    shelf_name = target_shelf.name
    api_response = api_shelf(request, target_shelf)
    referer = request.META.get(
        'HTTP-REFERER',
        reverse('user_home', args=[request.user.username]),
    )

    if request.method == 'POST':
        add_item_form = AddItem(request.user, request.POST)
    else:
        add_item_form = AddItemForm(request.user)
    shelf = json.loads(api_response.content)
    context = {
        'user': request.user,
        'shelf_user': target_user,
        'is_owner': request.user == target_user,
        'shelf_items': json.dumps(shelf['docs'], cls=DjangoJSONEncoder),
        'shelf_name': shelf_name,
        'shelf_slug': shelf['slug'],
        'add_item_form': add_item_form
    }
    context.update(csrf(request))

    if request.method == 'POST' and api_response.status_code == 200:
        messages.success(request, add_item_form.cleaned_data['title'] + ' has been added.')
    elif request.method in ('PATCH', 'PUT') and api_response.status_code == 200:
        messages.success(request, shelf_name + ' has been updated.')
        return redirect(referer)
    elif api_response.status_code == 204:
        messages.info(request, shelf_name + ' has been deleted.')
        return redirect(referer)
    elif api_response.status_code >= 400:
        return api_response

    return render_to_response('shelf/show.html', context)

def _serialize_shelves_with_items(shelves):
    return [_serialize_shelf(shelf) for shelf in shelves]

def _update_shelf_data(shelf, updates):
    updatables = ['name', 'description', 'is_public']
    for key, val in updates.items():
        if key in updatables:
            setattr(shelf, key, val)
    shelf.save()
    return shelf

def _serialize_shelf(shelf):
    item_list = []
    items = Item.objects.filter(shelf=shelf)

    for item in items:
        creators = Creator.objects.filter(item=item)
        creators_list = []
        for creator in creators:
            creators_list.append(creator.name)
        
        doc = {
            'item_uuid': str(item.item_uuid),
            'title': item.title,
            'creator': creators_list,
            'isbn': item.isbn,
            'web_location': item.link,
            'measurement_height_numeric': float(item.measurement_height_numeric),
            'measurement_page_numeric': item.measurement_page_numeric,
            'pub_date': item.pub_date,
            'shelfrank': item.shelfrank,
            'content_type': item.content_type,
            'creation_date': item.creation_date,
            'sort_order': item.sort_order
        }
        item_list.append(doc)

    return {
        'shelf_uuid': str(shelf.shelf_uuid),
        'user_name': shelf.user.username,
        'name': shelf.name,
        'description': shelf.description,
        'creation_date': shelf.creation_date,
        'is_public': shelf.is_public,
        'slug': shelf.slug,
        'docs': item_list,
        'start': -1,
        'num_found': len(item_list)
    }