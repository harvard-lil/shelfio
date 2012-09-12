import json

from lil.shelfio.views.roulette import api_shelf

from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.conf import settings


def welcome(request):
    """The application-wide welcome page."""
    
    if request.user.is_authenticated():
        # If no referrer or a referrer outside of shelfio or if user just logged in, send user to user page
        # TODO: clean up this logic and the sites business. it's nasty.
        
        site_name = str(Site.objects.get_current())
        
        if 'HTTP_REFERER' not in request.META or request.META['HTTP_REFERER'].find(site_name) == -1 or request.META['HTTP_REFERER'].find(settings.LOGIN_URL) >= 0:
            return HttpResponseRedirect(reverse('user_home', args=[request.user.username]))
        else:
            context = _create_full_welcome_context(request)
            return render_to_response('index.html',  context)


    context = _create_full_welcome_context(request)
    return render_to_response('index.html',  context)
        
        
def _create_full_welcome_context(request):
    """Get the random shelf from the Shelf Roulette API. Return the context."""
    
    api_response = api_shelf(request)
    random_shelf = json.loads(api_response.content)
    
    context = {
        'user': request.user,
        'shelf_user': random_shelf['user_name'],
        'shelf_items': json.dumps(random_shelf['docs'], cls=DjangoJSONEncoder),
        'shelf_name': random_shelf['name'],
        'shelf_slug': random_shelf['slug'],
    }

    return context