from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from lil.shelfio.models import Shelf, EditProfileForm, NewShelfForm
from django.utils.encoding import smart_unicode
import json
import httplib
import urllib
import urllib2
import logging


from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib import messages

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


@csrf_exempt
def api_search(request, target_type):
    """API to item search interface.
    """
    url = ELASTICSEARCH['HOST'] + target_type + '/_search'
    headers = {'Content-Type': 'application/json'}
    
    query = '*'
    if request.GET['q']:
        query = request.GET['q']
    
    start = 0
    if 'start' in request.GET:
        start = request.GET['start']

    limit = 10
    if 'limit' in request.GET:
        limit = request.GET['limit']
    
    query_string = {"query": query,
                    "default_operator": "AND"
                    }
    data = {"query": {"query_string": query_string},
            "from": start,
            "size": limit}
        
    req = urllib2.Request(url, json.dumps(data), headers)
    
    try: 
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
    except urllib2.HTTPError, e:
        print('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        print('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        print('HTTPException')
    except Exception:
        import traceback
        print('generic exception: ' + traceback.format_exc())
        
    
    jsoned_response = json.loads(response)
    hits = jsoned_response['hits']
    
    if target_type == 'item':
        packaged_hits = package_items(hits['hits'])
    if target_type == 'shelf':
        packaged_hits = package_shelves(hits['hits'])
    if target_type == 'user':
        packaged_hits = package_users(hits['hits'])
        
    packaged_hits['start'] = start
    packaged_hits['limit'] = limit
    packaged_hits['num_found'] = len(hits['hits'])
    
    return HttpResponse(json.dumps(packaged_hits, cls=DjangoJSONEncoder), mimetype='application/json')    

def package_items(hits):
    shaped_hits = []
    
    for hit in hits:
        shaped_hit = {}
        shaped_hit['id'] = hit['_id']
        shaped_hit['title'] = hit['_source']['title']
        shaped_hit['format'] = hit['_source']['format']
        shaped_hit['pub_date'] = hit['_source']['pub_date']
        shaped_hit['creator'] = hit['_source']['creator']
        shaped_hit['shelf'] = hit['_source']['shelf']
        
        if 'isbn' in hit['_source']:
            shaped_hit['isbn'] = hit['_source']['isbn']
        if 'notes' in hit['_source']:
            shaped_hit['notes'] = hit['_source']['notes']

        shaped_hits.append(shaped_hit)

    return {"docs": shaped_hits}

def package_shelves(hits):
    shaped_hits = []
    
    for hit in hits:
        shaped_hit = {}
        
        shaped_hit['id'] = hit['_id']
        shaped_hit['name'] = hit['_source']['name']
        shaped_hit['slug'] = hit['_source']['slug']
        shaped_hit['description'] = hit['_source']['description']
        shaped_hits.append(shaped_hit)

    return {"docs": shaped_hits}

def package_users(hits):
    shaped_hits = []
    
    for hit in hits:
        shaped_hit = {}
        
        shaped_hit['id'] = hit['_source']['username']
        shaped_hit['username'] = hit['_source']['username']
        
        if 'first_name' in hit['_source']:
            shaped_hit['first_name'] = hit['_source']['first_name']
        if 'last_name' in hit['_source']:
            shaped_hit['last_name'] = hit['_source']['last_name']
            
        shaped_hits.append(shaped_hit)

    return {"docs": shaped_hits}