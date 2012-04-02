from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from lil.shlvme.models import Shelf, Item, Creator, Tag, AddItemForm, CreatorForm
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.context_processors import csrf
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
from lil.shlvme.utils import fill_with_get
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def api_item_create(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    form = AddItemForm(request.user, request.POST)
    creator_form = CreatorForm(request.POST)
    if form.is_valid() and creator_form.is_valid():
        item = form.save()
        _save_creators(creator_form, item)
        return HttpResponse(json.dumps(serialize_item(item), cls=DjangoJSONEncoder), mimetype='application/json')
    else:
        return HttpResponse(status=400)

@csrf_exempt
def api_item_by_uuid(request, url_item_uuid):  
    if request.method == 'GET':
        try:
            item = Item.objects.get(item_uuid=url_item_uuid)
        except Item.DoesNotExist:
            return HttpResponse(status=404)
        except Item.MultipleObjectsReturned:
            return HttpResponse(status=500)

        shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
        if shelf.is_public or shelf.user == request.user:
            serialized_item = serialize_item(item)
            return HttpResponse(json.dumps(serialized_item, cls=DjangoJSONEncoder), mimetype='application/json')    
        return HttpResponse(status=404)

    
    if request.method == 'DELETE':
        try:
            item = Item.objects.get(item_uuid=url_item_uuid)
        except Item.DoesNotExist:
            return HttpResponse(status=404)
        except Item.MultipleObjectsReturned:
            return HttpResponse(status=500)
        shelf = Shelf.objects.get(shelf_uuid=item.shelf.shelf_uuid)
        if shelf.user == request.user:
            item.delete()
            return HttpResponse(status=204)
        return HttpResponse(status=404)

    if request.method in ['PUT', 'PATCH', 'POST']:
        pass


def user_create(request):    
    if not request.user.is_authenticated():
        messages.warning(request, 'You need to sign in to add items.')
        return redirect(reverse('process_login'))
    
    context = {}
    context.update(csrf(request))

    if request.method == 'GET':
        print request.GET
        add_item_form = AddItemForm(request.user)
        creator_form = CreatorForm()
        fill_with_get(add_item_form, request.GET)
        fill_with_get(creator_form, request.GET)

    elif request.method == 'POST':
        add_item_form = AddItemForm(request.user, request.POST)
        creator_form = CreatorForm(request.POST)
        if add_item_form.is_valid() and creator_form.is_valid():
            item = add_item_form.save()
            _save_creators(creator_form, item)
            success_text = '%(item)s added to %(shelf)s.' % {
                'item': add_item_form.cleaned_data['title'],
                'shelf': add_item_form.cleaned_data['shelf'].name
            }
            messages.success(request, success_text)
            return redirect(reverse(
                'user_shelf',
                args=[request.user.username, add_item_form.cleaned_data['shelf'].slug],
            ))

    context.update({
        'user': request.user,
        'add_item_form': add_item_form,
        'creator_form': creator_form
    })
    return render_to_response('item/create.html', context)

def serialize_item(item):
    serialized = {}
    for field in item._meta.fields:
        serialized[field.name] = getattr(item, field.name)
    serialized['item_uuid'] = str(item.item_uuid)
    serialized['shelf'] = str(item.shelf.shelf_uuid)
    creators = Creator.objects.filter(item=item)
    creators_list = [creator.name for creator in creators]
    serialized['creator'] = creators_list
    return serialized

def _save_creators(creator_form, item):
    creators = [c.strip() for c in creator_form.cleaned_data['creator'].split(',')]
    for creator in creators:
        c = Creator(name=creator, item=item)
        c.save()

