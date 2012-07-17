from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.conf import settings
import json
import random
from lil.shlvme.views.shelf import api_shelf
from lil.shlvme.models import Shelf

def welcome(request):
    """The application-wide welcome page."""
    
    if request.user.is_authenticated():
        # If no referrer or a referrer outside of shlvme or if user just logged in, send user to user page
        # TODO: clean up this logic and the sites business. it's nasty.
        
        site_name = str(Site.objects.get_current())
        
        if 'HTTP_REFERER' not in request.META or request.META['HTTP_REFERER'].find(site_name) == -1 or request.META['HTTP_REFERER'].find(settings.LOGIN_URL) >= 0:
            return HttpResponseRedirect(reverse('user_home', args=[request.user.username]))
        else:
            context = _create_full_welcome_context(request)
            return render_to_response('index.html',  context)
    else:
        context = _create_full_welcome_context(request)
        return render_to_response('index.html',  context)
        
        
def _create_full_welcome_context(request):
    # TODO: this is a temporary method for getting a shelf from the front page. implement a better approach 
    num_public_shelves = Shelf.objects.annotate(num_items=Count('item')).filter(num_items__gt=1).count()
    random_shelf = Shelf.objects.annotate(num_items=Count('item')).filter(num_items__gt=1)[random.randint(0, num_public_shelves - 1)]
            
    api_response = api_shelf(request, random_shelf)
        
    shelf = json.loads(api_response.content)

    context = {
        'user': request.user,
        'shelf_items': json.dumps(shelf['docs'], cls=DjangoJSONEncoder),
        'shelf_name': random_shelf.user.username + '\'s ' + random_shelf.name,
    }

    return context