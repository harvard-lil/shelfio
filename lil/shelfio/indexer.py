from django.utils.encoding import smart_unicode
import json
import httplib
import urllib
import urllib2
import logging
from lil.shelfio.fields import UUIDField
#from lil.shelfio.models import Creator

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


def index_user(user):
    """Receive a user model, pass it off to the elasticsearch indexer
    """
    
    #Usernames are unique, so use them instead of a UUID to avoid a DB call    
    data = {
            '_id': user.username,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
            }
    
    expand_the_waistband('user', data)

def index_shelf(shelf):
    """Receive a shelf model, pass it off to the elasticsearch indexer
    """

    data = {'_id': smart_unicode(shelf.shelf_uuid),
            'name': shelf.name,
            'slug': shelf.slug,
            'description': shelf.description
            }
    
    expand_the_waistband('shelf', data)

def index_item(item):
    """Receive an item model, pass it off to the elasticsearch indexer
    """
    
    from lil.shelfio.models import Creator
    creators = Creator.objects.filter(item=item.id)
    creators_list = [creator.name for creator in creators]

    data = {'_id': smart_unicode(item.item_uuid),
            'title': item.title,
            'creator': creators_list,
            'link': item.link,
            'format': item.format,
            'pub_date': item.pub_date,
            'isbn': item.isbn,
            'notes': item.notes
            }
    
    expand_the_waistband('item', data)
    
    

def expand_the_waistband(index_name, data):
    """Send to elasticsearch. Expand that elastic waistband"""
    
    url = ELASTICSEARCH['HOST'] + index_name + '/' + data['_id']
    headers = {'Content-Type': 'application/json'}
    
    # Trim the ID because it causes ES to blow up
    del data['_id']
    
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
        
def unindex_user(user):
    """Receive a user model, pass it onto the ElastiSearch interface
    """
    
    #Usernames are unique, so use them instead of a UUID to avoid a DB call    
    data = {'_id': user.username}
    
    shrink_the_waistband('user', data)

def unindex_shelf(shelf):
    """Receive a shelf model, pass it onto the ElastiSearch interface
    """

    data = {'_id': smart_unicode(shelf.shelf_uuid)}
    
    shrink_the_waistband('shelf', data)

def unindex_item(item):
    """Receive an item model, pass it onto the ElastiSearch interface
    """

    data = {'_id': smart_unicode(item.item_uuid)}
    
    shrink_the_waistband('item', data)
        
def shrink_the_waistband(index_name, data):
    """Remove from elasticsearch. Tighten that belt, sonny. (Delete from elasticsearch)"""

    url = ELASTICSEARCH['HOST'] + index_name + '/' + data['_id']
    
    conn = httplib.HTTPConnection(url)
    conn.request('DELETE', url) 
    resp = conn.getresponse()
    content = resp.read()
        
