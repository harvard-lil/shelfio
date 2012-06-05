from django.shortcuts import redirect
from django.core.urlresolvers import reverse
import re
import logging
import urllib
import urllib2
import json
from xml.etree.ElementTree import fromstring, ElementTree
from BeautifulSoup import BeautifulSoup
import bottlenose
from lxml import objectify


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
    aws_associate_tag = AMZ['ASSOCIATE_TAG']
    
    details = {}
    
    amazon = bottlenose.Amazon(aws_key, aws_secret_key, aws_associate_tag)
    response = amazon.ItemLookup(ItemId=asin, ResponseGroup="Large", IdType="ASIN")
    
    root = objectify.fromstring(response)
    
    if root.Items.Item.ItemAttributes is not None:
        if root.Items.Item.ItemAttributes.Author is not None:
            details['creator'] = root.Items.Item.ItemAttributes.Author
        if root.Items.Item.ItemAttributes.Title is not None:
            details['title'] = root.Items.Item.ItemAttributes.Title
        if root.Items.Item.ItemAttributes.ISBN is not None:
            details['key'] = 'isbn'
            details['value'] = root.Items.Item.ItemAttributes.ISBN.text
            print details['value']
        if root.Items.Item.ItemAttributes.NumberOfPages is not None:
            details['measurement_page_numeric'] = root.Items.Item.ItemAttributes.NumberOfPages
        if root.Items.Item.ItemAttributes.ItemDimensions is not None and root.Items.Item.ItemAttributes.ItemDimensions['Length'] is not None :
            amz_length = int(root.Items.Item.ItemAttributes.ItemDimensions['Length'])
            height_in_inches = (amz_length / 100) * 2.54
            details['measurement_height_numeric'] = height_in_inches
        if root.Items.Item.ItemAttributes.ProductGroup is not None:
            details['format'] = 'book'
        if root.Items.Item.ItemAttributes.PublicationDate is not None:
            pub_date = root.Items.Item.ItemAttributes.PublicationDate
            
            if len(pub_date) > 4: 
                details['pub_date'] = pub_date[0:5]
        
        
    return details

def get_imdb_details(url):
    """Given an IMDB URL, get title, creator, etc. from imdapi.com
    """
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    
    # Use Beautiful Soup to create a workable object from the source
    soup = BeautifulSoup(response)
    
    # This title contains our title and year
    title = soup.find("h1",{"class":"header", "itemprop": "name"})

    release_year = title.span.a.string
    
    # Year is in the span. Remove it so that we only have the title left 
    title.span.decompose()   
    cleaned_title = re.sub(r'\n', '', title.contents[0])
    
    director = soup.find("a",{"itemprop": "director"}).string

    details = {}
    details['title'] = cleaned_title
    details['format'] = 'Video/Film'
    details['creator'] = director
    details['pub_date'] = release_year
    
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