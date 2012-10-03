import json
import logging

from lil.shelfio.models import Shelf, Item, NewShelfForm
from lil.shelfio.views.api.v1.item import serialize_item

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

@csrf_exempt
def api_shelf_create(request):
    if request.method == 'POST' and request.user.is_authenticated():
        form = NewShelfForm(request.POST)
        if form.is_valid():
            try:
                shelf = Shelf(
                    user=request.user,
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'],
                    is_private=form.cleaned_data['is_private'],
                )
                shelf.save()
            except ValidationError, e:
                return HttpResponse('A shelf by that name already exists.', status=409)
        else:
            return HttpResponse('Shelf name is required.', status=400)
        

        serialized = serialize_shelf(shelf)
        
        return HttpResponse(json.dumps(serialized, cls=DjangoJSONEncoder), mimetype='application/json', status=201,)

    # POST but not authenticated
    elif request.method == 'POST':
        return HttpResponse(status=401)

    # Method not supported
    else:
        return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def api_shelf_by_uuid(request, url_shelf_uuid):
    # /shelf.io/api/shelf/5138a693-7ea9-4f3a-8e4f-40ad3b847ef9
    shelf = get_object_or_404(Shelf, shelf_uuid=url_shelf_uuid)
    return api_shelf(request, shelf)

@csrf_exempt
def api_shelf_by_name(request, url_user_name, url_shelf_slug):
    # /shelf.io/api/shelf/some-username/some-shelf-slug
    target_user = get_object_or_404(User, username=url_user_name)
    shelf = get_object_or_404(Shelf, user=target_user, slug=url_shelf_slug)

    return api_shelf(request, shelf)

def api_shelf(request, shelf):
    if request.user != shelf.user and shelf.is_private:
        return HttpResponse(status=404)

    # Edit shelf
    elif request.rfc5789_method in ['PUT', 'POST'] and request.user.is_authenticated():
        try:
            serialized = serialize_shelf(_update_shelf_data(shelf, request.POST))
        except ValidationError, e:
            return HttpResponse('You already have a shelf by that name.', status=400)
        return HttpResponse(
            json.dumps(serialized, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )
        

    # Delete shelf
    elif request.rfc5789_method == 'DELETE' and request.user.is_authenticated():
        shelf.delete()
        return HttpResponse(status=204)

    elif request.method == 'GET':
        serialized_shelf = serialize_shelf(shelf)
        return HttpResponse(
            json.dumps(serialized_shelf, cls=DjangoJSONEncoder),
            mimetype='application/json',
        )

    else:
        return HttpResponseNotAllowed(['POST', 'PUT', 'DELETE', 'GET'])

def _update_shelf_data(shelf, updates):
    form = NewShelfForm(updates)
    if form.is_valid():
        updatables = ['name', 'description']
        for key, val in updates.items():
            if key in updatables:
                setattr(shelf, key, val)

        setattr(shelf, 'is_private', updates.has_key('is_private'))
        
        shelf.save()
        return shelf
    else:
        raise ValidationError('Shelf name is required')

def serialize_shelf(shelf):
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