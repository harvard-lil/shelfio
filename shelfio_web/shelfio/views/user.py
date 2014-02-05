import logging

from shelfio import indexer
from shelfio.models import Shelf, FavoriteUser, EditProfileForm, NewShelfForm
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib import messages

logger = logging.getLogger(__name__)

def user_home(request, user_name):
    """A user's home. Includes profile and list of shelves."""
    context = _get_user_data(request, user_name)
    context.update(csrf(request))
    context.update({ 'user': request.user, 'new_shelf_form': NewShelfForm() })
    context.update({ 'profileform': EditProfileForm(context)})

    # Modify user profile
    if request.rfc5789_method in ['PUT', 'PATCH', 'POST']:
        profileform = EditProfileForm(request.POST)

        if not request.user.is_authenticated():
            return HttpResponse(status=401)
        elif user_name != request.user.username:
            return HttpResponse(status=403)
        
        if profileform.is_valid():
            _update_user_data(user_name, request.POST)
            return redirect(reverse('user_home', args=[user_name]))
        
        context['profileform'] = profileform

    # User creates new shelf
    elif request.method == 'POST':
        new_shelf_form = NewShelfForm(request.POST)

        if new_shelf_form.is_valid():
            new_shelf = Shelf(
                user=request.user,
                name=new_shelf_form.cleaned_data['name'],
                description=new_shelf_form.cleaned_data['description'],
                is_private=new_shelf_form.cleaned_data['is_private'],
            )
            try:
                new_shelf.save()
            except ValidationError:
                messages.error(request, 'A shelf with that name already exists.')
            return redirect(request.path)

        context['new_shelf_form'] = new_shelf_form
        
    context['messages'] = messages.get_messages(request);
    return render_to_response('user/show.html', context)

@csrf_exempt
def helpers(request, user_name):
    """Some user helpers"""
    
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    
    # If the user kills the "welcome, here's the bookmarklet" box on their home page:        
    if request.POST['show-welcome'] == 'False':
        profile = request.user.get_profile()
        profile.display_welcome = False
        profile.save()

        #user.save()
        return HttpResponse(status=204)

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
        })
    else:
        shelf_query.exclude(is_private=True)

    for shelf in shelf_query:
        shelf_to_serialize = {
            'shelf_uuid': str(shelf.shelf_uuid),
            'name': shelf.name,
            'slug': shelf.slug,
            'description': shelf.description,
            'creation_date': shelf.creation_date,
            'is_private': shelf.is_private
        }
        shelves.append(shelf_to_serialize)
        
    favorite_user_flag = False
        
    if request.user.is_authenticated():
        favorite_user = FavoriteUser.objects.filter(leader=target_user).filter(follower=request.user)
        favorite_user_flag = len(favorite_user) == 1

    context.update({
        'is_owner': is_owner,
        'is_favorite': favorite_user_flag,
        'user_name': target_user.username,
        'email': target_user.email,
        'docs': shelves,
        'SHELFIO_API_LOCATION': settings.SHELFIO_API['LOCATION'],

    })

    return context

def _update_user_data(user_name, updates):
    target_user = get_object_or_404(User, username=user_name)
    updatables = ['first_name', 'last_name', 'email']
    for key, val in updates.items():
        if key in updatables:
            setattr(target_user, key, val)    
    target_user.full_clean()
    target_user.save()
    
    # Index when a user updates their first or last name
    indexer.index_user(target_user)
