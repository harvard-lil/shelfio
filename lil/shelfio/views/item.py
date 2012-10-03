import logging
import urllib

from lil.shelfio.utils import fill_with_get

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from lil.shelfio.models import Shelf, Creator, AddItemForm, CreatorForm
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.context_processors import csrf


logger = logging.getLogger(__name__)

def user_create(request):
        
    if not request.user.is_authenticated():
        messages.warning(request, 'You need to sign in to add items.')
        #return redirect(reverse('process_login'))
        return redirect_to_login(urllib.quote_plus(request.get_full_path()))
   
    context = {}
    context.update(csrf(request))
       
    if request.method == 'GET':
        
        add_item_form = AddItemForm(request.user)
        creator_form = CreatorForm()
        fill_with_get(add_item_form, request.GET)
        fill_with_get(creator_form, request.GET)

    elif request.method == 'POST':
        # A user can create a new shelf while adding an item      
        if 'new_shelf_name' in request.POST:
            new_shelf = Shelf(
                user=request.user,
                name = request.POST['new_shelf_name'],
                description = request.POST['new_shelf_description'],
                is_private = request.POST['new_shelf_is_private'],
            )
            try:
                new_shelf.save()
            except ValidationError:
                messages.error(request, 'A shelf with that name already exists.')
            return redirect(request.path)
        
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
        'messages': messages.get_messages(request),
        'user': request.user,
        'add_item_form': add_item_form,
        'creator_form': creator_form
    })
    return render_to_response('item/create.html', context)

def _save_creators(creator_form, item):
    creators = [c.strip() for c in creator_form.cleaned_data['creator'].split(',')]
    for creator in creators:
        c = Creator(name=creator, item=item)
        c.save()