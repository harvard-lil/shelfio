from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models import Count
import json
import random
from lil.shlvme.views.shelf import api_shelf
from lil.shlvme.models import Shelf

def welcome(request):
    """The application-wide welcome page."""
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_home', args=[request.user.username]))
    else:
        # TODO: this is a temporary method for getting a shelf from the front page. implement a better approach 
        num_public_shelves = Shelf.objects.annotate(num_items=Count('item')).filter(num_items__gt=1).count()
        random_shelf = Shelf.objects.annotate(num_items=Count('item')).filter(num_items__gt=1)[random.randint(0, num_public_shelves - 1)]
                
        api_response = api_shelf(request, random_shelf)
            
        shelf = json.loads(api_response.content)
        print shelf

        context = {
            'user': request.user,
            #'shelf_user': target_user,
            #'is_owner': request.user == target_user,
            'shelf_items': json.dumps(shelf['docs'], cls=DjangoJSONEncoder),
            'shelf_name': random_shelf.user.username + '\'s ' + random_shelf.name,
            #'shelf_slug': shelf['slug'],
            #'shelf_domain' : Site.objects.get_current().domain,
            #'shelf_description': shelf['description']
        }
        #context.update(csrf(request))
    
        
        return render_to_response('index.html',  context)