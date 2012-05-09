from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from amazonproduct import API
import re
import logging
import urllib
import urllib2
import json
from xml.etree.ElementTree import fromstring, ElementTree

logger = logging.getLogger(__name__)

try:
    from lil.shlvme.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

def incoming(request):
    url = request.GET.get('loc', None)

    details = {}
    
    if re.search(r'amazon\.com', url):
        details = get_amazon_details(url)

    elif re.search(r'imdb\.com', url):
        details = get_imdb_details(url)

    elif re.search(r'musicbrainz\.org', url):
        details = get_musicbrainz_details(url)
        
    details['link'] = url
    encoded_params = urllib.urlencode(details)

    return redirect(reverse('user_item_create') + '?' + encoded_params)
    
def get_amazon_details(url):
    """Given an Amazon URL, get title, creator, etc. from imdapi.com
    """
    matches = re.search(r'\/([A-Z0-9]{10})($|\/)', url)
    asin = matches.group(1)

    aws_key = AMZ['KEY']
    aws_secret_key = AMZ['SECRET_KEY']
    api = API(aws_key, aws_secret_key, 'us')
    
    details = {}
    
    looked_up_item = api.item_lookup(asin, IdType='ASIN', AssociateTag= AMZ['ASSOCIATE_TAG'], ResponseGroup='Large')

    if looked_up_item['Items']['Item']['ItemAttributes'] is not None:
        item_attributes = looked_up_item['Items']['Item']['ItemAttributes']
        
        if hasattr(item_attributes, 'Author'):
            details['creator'] = item_attributes['Author']
        if hasattr(item_attributes, 'Title'):
            details['title'] = item_attributes['Title']
        if hasattr(item_attributes, 'ISBN'):
            details['isbn'] = item_attributes['ISBN']
        if hasattr(item_attributes, 'NumberOfPages'):
            details['measurement_page_numeric'] = item_attributes['NumberOfPages']
        if hasattr(item_attributes, 'ItemDimensions') and hasattr(item_attributes['ItemDimensions'], 'Length'):
            amz_length = int(item_attributes['ItemDimensions']['Length'])
            height_in_inches = (amz_length / 100) * 2.54
            details['measurement_height_numeric'] = height_in_inches
        if hasattr(item_attributes, 'Author'):
            details['format'] = 'book' #item_attributes['ProductGroup']
        if hasattr(item_attributes, 'PublicationDate'):
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
    details['format'] = 'Video/Film'
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
    details['format'] = 'soundrecording'
    details['creator'] = name_element.text
    details['pub_date'] = date_element.text
    
    return details