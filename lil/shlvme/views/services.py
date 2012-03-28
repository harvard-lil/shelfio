from django.shortcuts import render_to_response
from amazonproduct import API
import re
import logging
import urllib
import urllib2
import json
from xml.etree.ElementTree import fromstring, ElementTree

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
    
    if re.search(r'amazon\.com', url):
        details = get_amazon_details(url)
        return render_to_response('add-item.html', {'user': request.user, 'creator': details['creator'], 'title': details['title'], 
                                                    'isbn': details['isbn'], 'measurement_page_numeric': details['measurement_page_numeric'],
                                                    'measurement_height_numeric': details['measurement_height_numeric'],
                                                    'content_type': details['content_type'], 'pub_date': details['pub_date'],
                                                    'link': url, 'creator': details['creator']})

    elif re.search(r'imdb\.com', url):
        details = get_imdb_details(url)
        return render_to_response('add-item.html', {'user': request.user, 'title': details['title'],
                                                    'link': url, 'content_type': details['content_type'],
                                                    'creator': details['creator'], 'pub_date': details['pub_date']})

    elif re.search(r'musicbrainz\.org', url):
        details = get_musicbrainz_details(url)
        return render_to_response('add-item.html', {'user': request.user, 'title': details['title'],
                                                    'link': url, 'content_type': details['content_type'],
                                                    'creator': details['creator'], 'pub_date': details['pub_date']})
def get_amazon_details(url):
    """Given an IMDB URL, get title, creator, etc. from imdapi.com
    """
    matches = re.search(r'\/([A-Z0-9]{10})($|\/)', url)
    asin = matches.group(1)

    aws_key = AMZ['KEY']
    aws_secret_key = AMZ['SECRET_KEY']
    api = API(aws_key, aws_secret_key, 'us')
    
    details = {}
    
    looked_up_item = api.item_lookup(asin, IdType='ASIN', AssociateTag= AMZ['ASSOCIATE_TAG'], ResponseGroup='Large')
    item_attributes = looked_up_item['Items']['Item']['ItemAttributes']
                   
    details['creator'] = item_attributes['Author']
    details['title'] = item_attributes['Title']
    details['isbn'] = item_attributes['ISBN']
    details['measurement_page_numeric'] = item_attributes['NumberOfPages']
    details['measurement_height_numeric'] = item_attributes['ItemDimensions']['Length']
    details['content_type'] = item_attributes['ProductGroup']
    details['pub_date'] = item_attributes['PublicationDate']
        
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

def get_musicbrainz_details(url):
    """Given an musicbrainz URL, get title, creator, etc.
    """
    
    # Look for something like http://musicbrainz.org/release-group/20e845b1-c6b5-44f7-ab7e-cbc0e33767b5
    # or http://musicbrainz.org/release/b21c3cb7-a82d-4d9d-aef7-56569ca734be
    # See http://musicbrainz.org/doc/XML_Web_Service/Version_2#Lookups

    matches = re.search(r'musicbrainz\.org/([a-zA-Z\-]+)/([0\w\-]+)', url)

    mb_resource = matches.group(1)
    mb_id = matches.group(2)
    
    details = {}

    url = 'http://musicbrainz.org/ws/2/' + mb_resource + '/' + mb_id
    url_params = {'inc' : 'artists'}
    data = urllib.urlencode(url_params)
    url = url + '?' + data
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    raw_response = response.read()
    
    tree = ElementTree(fromstring(raw_response))
    namespace = "{http://musicbrainz.org/ns/mmd-2.0#}"
    title_element = tree.find('*/{0}title'.format(namespace))
    name_element = tree.find('*/{0}artist-credit/{0}name-credit/{0}artist/{0}name'.format(namespace))
    date_element = tree.find('*/{0}date'.format(namespace))
    
    # If we don't find the date (date element only occurs in the release type), try
    # the first-release-date.
    # TODO: There's probably a clever xpath way to do this 
    if date_element is None:
        date_element = tree.find('*/{0}first-release-date'.format(namespace))

    details['title'] = title_element.text
    details['content_type'] = 'music'
    details['creator'] = name_element.text
    details['pub_date'] = date_element.text
    
    return details