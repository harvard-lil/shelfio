from django.shortcuts import render_to_response
from amazonproduct import API
import re
import logging
import urllib
import urllib2
import json
from lxml.etree import tostring

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


def incoming(request):
    url = request.GET.get('loc', None)
    
    if re.search(r'imdb\.com', url):
        details = get_imdb_details(url)
        return render_to_response('add-item.html', {'user': request.user, 'title': details['title'],
                                                    'link': url, 'content_type': details['content_type'],
                                                    'creator': details['creator'], 'pub_date': details['pub_date']})
    elif re.search(r'amazon\.com', url):
        details = get_amazon_details(url)
        return render_to_response('add-item.html', {'user': request.user, 'title': details['title'],
                                                    'link': url, 'creator': details['creator']})

def get_amazon_details(url):
    """Given an IMDB URL, get title, creator, etc. from imdapi.com
    """
    matches = re.search(r'\/([A-Z0-9]{10})($|\/)', url)
    asin = matches.group(1)

    aws_key = AMZ['KEY']
    aws_secret_key = AMZ['SECRET_KEY']
    api = API(aws_key, aws_secret_key, 'us')
    
    details = {}
    
    for root in api.item_lookup(asin, IdType='ASIN', AssociateTag= AMZ['ASSOCIATE_TAG'], ResponseGroup='Large'):
        logger.info( tostring(root, pretty_print=True))
        nspace = root.nsmap.get(None, '')
        amazon_items = root.xpath('//aws:Items/aws:Item', namespaces={'aws' : nspace})

        for amazon_item in amazon_items:
            #logger.info(dir(amazon_item['ItemAttributes']))
            if hasattr(amazon_item.ItemAttributes, 'Author'): 
                details['creator'] = unicode(amazon_item.ItemAttributes.Author)

            if hasattr(amazon_item.ItemAttributes, 'Title'): 
                details['title'] = unicode(amazon_item.ItemAttributes.Title)

    details['link'] = url
    #details['content_type'] = 'dvd'
    #details['pub_date'] = response_json['Year']
    
    return details
    

def get_imdb_details(url):
    """Given an IMDB URL, get title, creator, etc. from imdapi.com
    """
    matches = re.search(r'/([a-zA-Z]{2}[0-9]{7})', url)
    imdb_id = matches.group(1)
    
    details = {}

    url = 'http://www.imdbapi.com/'
    url_params = {'i' : imdb_id}

    data = urllib.urlencode(url_params)
    url = url + '?' + data
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    response_json = json.loads(response.read())

    details['title'] = response_json['Title']
    details['link'] = url
    details['content_type'] = 'dvd'
    details['creator'] = response_json['Director']
    details['pub_date'] = response_json['Year']
    
    return details