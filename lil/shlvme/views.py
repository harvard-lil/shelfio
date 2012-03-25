#from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from lil.shlvme.models import Shelf, Item, Creator, Tag, LoginForm
import json
from amazonproduct import API
import re
#from django.forms.formsets import formset_factory
from django.core.context_processors import csrf
#import random
from django.contrib import auth
from django.contrib.auth.models import User
import logging

try:
    from lil.shlvme.local_settings import *
except ImportError, e:
    print 'Unable to load local_settings.py:', e

logger = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
    filename = '/tmp/shlvme.log',
    filemode = 'w'
)

########################################
###### Pages ###########################
########################################

def user_home(request, user_name):
    """A user's home. Includes profile and list of shelves."""
    if request.method == 'GET':
        context = _get_user_data(request, user_name)
        context['user'] = request.user
        context.update(csrf(request))
        return render_to_response('user/show.html', context)

    elif request.method == 'POST' and request.POST.get('_method').upper() == 'PATCH':
        if not request.user.is_authenticated():
            return HttpResponse(status=401)
        elif user_name != request.user.username:
            return HttpResponse(status=403)

        try:
            _update_user_data(user_name, request.POST)
        except ValidationError, e:
            return HttpResponse(status=400)
        return redirect(reverse('user_home', args=[user_name]))

def user_shelf(request, url_user_name, url_shelf_name):
    """A user's shelf."""
    return render_to_response('user_shelf.html', {'user_name': url_user_name, 'shelf_name': url_shelf_name, 'user': request.user})

def welcome(request):
    """The application-wide welcome page."""
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_home', args=[request.user.username]))
    else:
        return render_to_response('index.html', {'user': request.user})


########################################
###### APIs ############################
########################################

@csrf_exempt
def api_user(request, url_user_name):
    """API for users
     Accessed using something like shlv.me/api/user/obama
     TODO: we need to validate/clean/urldecode the GET/POST values ?
    """
    if request.method == 'GET':                
        context = _get_user_data(request, url_user_name)
        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), mimetype='application/json')
    
    # If the user updates her profile, handle it here
    if (request.method == 'POST' or request.method == 'PATCH'):
        if not request.user.is_authenticated():
            return HttpResponse(status=401)
        elif request.user.username != url_user_name:
            return HttpResponse(status=403)

        try:
            _update_user_data(url_user_name, request.POST)
        except ValidationError, e:
            # Should an invalid update be a 400 (Bad Request) response?
            return HttpResponse(status=400)
        _get_user_data(request, url_user_name)
        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), mimetype='application/json')

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

            docs = serialize_shelves_with_items(shelves)
        else:
            shelves = Shelf.objects.filter(is_public=True).filter(shelf_uuid=url_shelf_uuid)

            docs = serialize_shelves_with_items(shelves)

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
            
            docs = serialize_shelves_with_items(shelves)
           
        else:
            target_user = User.objects.get(username=url_user_name)
            shelves = Shelf.objects.filter(user=target_user).filter(name=url_shelf_name).filter(is_public=True)
            
            docs = serialize_shelves_with_items(shelves)
        
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
        
@csrf_exempt
def api_tag(request, url_tag_uuid=None):
    """API for tags
    Something like shlv.me/api/tag/7838a693-7ea9-4f3a-8e4f-40ad3b8492e3
    TODO: we need to validate/clean/urldecode the GET/POST values
    """
    
    # Add a new tag to an item
    # TODO: All kinds of validation. Also, some type of transaction so that the item and creator are saved together?
    if request.method == 'POST' and request.user.is_authenticated():
        target_user = User.objects.get(username=request.user.username)
        target_item = Item.objects.get(item_uuid=request.POST.get('item-uuid'))
        target_shelf = Shelf.objects.get(shelf_uuid = target_item.shelf.shelf_uuid)
        
        if target_shelf.user == request.user:
            staged_tag = Tag(item=target_item, key=request.POST.get('tag-key'), value=request.POST.get('tag-value'))
            staged_tag.save()
            
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=401)
        
    else:
        return HttpResponse(status=401)
    
    # Delete an existing tag
    if request.method == 'DELETE' and request.user.is_authenticated() and url_tag_uuid is not None:
        # TODO Fix. This feels so wrong:
        target_tag = Tag.objects.get(tag_uuid = url_tag_uuid)
        target_item = Item.objects.get(item_uuid = target_tag.item.item_uuid)
        target_shelf = Shelf.objects.get(shelf_uuid = target_item.shelf.shelf_uuid)
        target_user = User.objects.get(username = target_shelf.user.username)
    
        # Get tags for item that user owns
        if request.user.is_authenticated():
            
            # User owns the shelf
            if target_shelf.user == target_user:
                target_tag.delete()
                return HttpResponse(status=202)
                
            else:
                return HttpResponse(status=401)

        
    # Edit an existing shelf
    elif request.method == 'POST' and request.user.is_authenticated() and url_tag_uuid is not None:
        return HttpResponse(status=202)

    # Get tags for an item
    elif request.method == 'GET' and request.user.is_authenticated() and url_tag_uuid is not None:
        pass
    
    # TODO: trap errors
    # try:
    #     p = Publisher.objects.get(name='Apress')
    # except Publisher.DoesNotExist:
    #    print "Apress isn't in the database yet."
    # else:
    #     print "Apress is in the database."
    

#######################
###### Auth/Auth ######
#######################

# TODO: a lot of the auth/auth functionality is crude. cleanup.

def process_register(request):
    """Register a new user"""
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            supplied_username = request.POST.get('username', '')
            supplied_password = request.POST.get('password1', '')
            user = auth.authenticate(username=supplied_username, password=supplied_password)
            
            auth.login(request, user)
            return HttpResponseRedirect(reverse('user_home', args=[user.username]))
    else:
        form = UserCreationForm()
        c = {}
        c.update(csrf(request))
        c.update({'form': form})
        return render_to_response("register.html", c)


def process_login(request):
    """The login handler"""
    
    # If we get a GET, send the login form
    if request.method == 'GET':
        if not request.user.is_authenticated():
            formset = LoginForm()
            
            c = {}
            c.update(csrf(request))
            c.update({'formset': formset})
            return render_to_response('login.html', c)
        else:
            return redirect(reverse('welcome'))

    # If we get a POST, someone has filled out the login form
    if request.method == 'POST':
        supplied_username = request.POST['username']
        supplied_password = request.POST['password']
        user = auth.authenticate(username=supplied_username, password=supplied_password)
        
        formset = LoginForm(initial={'username': supplied_username})
        c = {}
        c.update(csrf(request))
        c.update({'formset': formset})
        
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect(reverse('user_home', args=[user.username]))
            else:
                return render_to_response('login.html', c)
        else:
            return render_to_response('login.html', c)

def process_logout(request):
    """The logout handler"""
    
    if request.user.is_authenticated():
        auth.logout(request)
    
    return redirect(reverse('welcome'))


########################################
###### Services ########################
########################################

def services_incoming(request):
    """We have an incoming item (probably from the bookmarklet)"""
    
    #TODO: this is nothing more than a test now. cleanup.
    url = request.GET.get('loc', None)
    matches = re.search(r'\/([A-Z0-9]{10})($|\/)', url)
    asin = matches.group(1)
    
    aws_key = AMZ.KEY 
    aws_secret_key = AMZ.SECRET_KEY 
    api = API(aws_key, aws_secret_key, 'us')
    
    for root in api.item_lookup(asin, IdType='ASIN', AssociateTag= AMZ.ASSOCIATE_TAG):
        nspace = root.nsmap.get(None, '')
        amazon_items = root.xpath('//aws:Items/aws:Item', namespaces={'aws' : nspace})
        author = u'Unknown'
        title = u'Unknown'
        isbn = u'Unknown'

        for amazon_item in amazon_items:
            if hasattr(amazon_item.ItemAttributes, 'Author'): 
                author = unicode(amazon_item.ItemAttributes.Author)

            if hasattr(amazon_item.ItemAttributes, 'Title'): 
                title = unicode(amazon_item.ItemAttributes.Title)
    
    return render_to_response('add-item.html', {'user': request.user, 'creator': author, 'title': title, 'isbn': isbn})



########################################
###### Local Helpers ###################
########################################

def serialize_shelves_with_items(shelves):
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

def get_public_tags(url_item_uuid):
    target_item = Item.objects.get(item_uuid = url_item_uuid)
    target_tags = Tag.objects.filter(item = target_item)
    return target_tags

def serialize_tags(tags):
    docs = []

    for tag in tags:
        doc = {}
        doc['tag_uuid'] = str(tag.tag_uuid)
        doc['tag_key'] = tag.key
        doc['tag_value'] = tag.value
        docs.append(doc)
        
    return docs

def _get_user_data(request, user_name):
    context = {}
    target_user = get_object_or_404(User, username=user_name)
    queried_shelves = Shelf.objects.filter(user=target_user)
    is_owner = target_user.username == request.user.username and request.user.is_authenticated()
    shelf_query = Shelf.objects.filter(user=target_user)
    shelves = []
    
    if is_owner:
        context.update({
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'date_joined': target_user.date_joined,
            'email': target_user.email
        })
    else:
        shelf_query.exclude(is_public=True)

    for shelf in shelf_query:
        shelf_to_serialize = {
            'shelf_uuid': str(shelf.shelf_uuid),
            'name': shelf.name,
            'description': shelf.description,
            'creation_date': shelf.creation_date,
            'is_public': shelf.is_public
        }
        shelves.append(shelf_to_serialize)

    context.update({
        'is_owner': is_owner,
        'user_name': target_user.username,
        'docs': shelves
    })

    return context

def _update_user_data(user_name, updates):
    target_user = get_object_or_404(User, username=user_name)
    updatables = ['first_name', 'last_name', 'email']
    for key in updatables:
        setattr(target_user, key, updates[key])
    target_user.full_clean()
    target_user.save()


