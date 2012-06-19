from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template import RequestContext
import re
import logging
import urllib
import urllib2
import json
from xml.etree.ElementTree import fromstring, ElementTree
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
import bottlenose
from lxml import objectify
from lil.shlvme.utils import get_year_from_raw_date, get_numeric_page_count

logger = logging.getLogger(__name__)

try:
    from lil.shlvme.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

def incoming(request):
    """Regex the url and if we find something we support, pass it off to that
       handler. If it bombs, catch the exception and send to to the generic
       webpage handler (add it as a webpage instead of book or DVD or ...)"""
       
    url = request.GET.get('loc', None)

    details = {}
    
    if re.search(r'amazon\.com', url):
        try:
            details = get_amazon_details(url)
        except:
            details = get_web_resource(url)
            messages.warning(request, "We tried hard to process the Amazon page you just sent us, but we think we missed some things. Sorry. Here's our best guess.")

    elif re.search(r'imdb\.com', url):
        try:
            details = get_imdb_details(url)
        except:
            details = get_web_resource(url)
            messages.warning(request, "We tried hard to process the IMDB page you just sent us, but we think we missed some things. Sorry. Here's our best guess.")

    elif re.search(r'musicbrainz\.org', url):
        try:
            details = get_musicbrainz_details(url)
        except:
            details = get_web_resource(url)
            messages.warning(request, "We tried hard to process the MusicBrainz page you just sent us, but we think we missed some things. Sorry. Here's our best guess.")
        
    elif re.search(r'goodreads\.com', url):
        try:
            details = get_goodreads_details(url)
        except:
            details = get_web_resource(url)
            messages.warning(request, "We tried hard to process the Goodreads page you just sent us, but we think we missed some things. Sorry. Here's our best guess.")
        
    elif re.search(r'openlibrary\.org', url):
        try:
            details = get_openlibrary_details(url)
        except:
            details = get_web_resource(url)
            messages.warning(request, "We tried hard to process the Open Library page you just sent us, but we think we missed some things. Sorry. Here's our best guess.")
        
    else:
        details = get_web_resource(url)
        
    details['link'] = url
    encoded_params = urllib.urlencode(details)
    
    return redirect(reverse('user_item_create') + '?' + encoded_params, context_instance=RequestContext(request))

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
       
    if hasattr(root.Items.Item.ItemAttributes, 'Author'):
        details['creator'] = root.Items.Item.ItemAttributes.Author
    elif hasattr(root.Items.Item.ItemAttributes, 'Artist'):
        details['creator'] = root.Items.Item.ItemAttributes.Artist
    elif hasattr(root.Items.Item.ItemAttributes, 'Director'):
        details['creator'] = root.Items.Item.ItemAttributes.Director

    if hasattr(root.Items.Item.ItemAttributes, 'Title'):
        details['title'] = root.Items.Item.ItemAttributes.Title
    if hasattr(root.Items.Item.ItemAttributes, 'ISBN'):
        details['isbn'] = root.Items.Item.ItemAttributes.ISBN.text
    if hasattr(root.Items.Item.ItemAttributes, 'NumberOfPages'):
        details['measurement_page_numeric'] = root.Items.Item.ItemAttributes.NumberOfPages
    if hasattr(root.Items.Item.ItemAttributes, 'PackageDimensions') and hasattr(root.Items.Item.ItemAttributes.PackageDimensions, 'Length'):
        amz_length = int(root.Items.Item.ItemAttributes.PackageDimensions['Length'])
        height_in_inches = '{0:.2g}'.format((amz_length / 100.0) * 2.54)
        details['measurement_height_numeric'] = height_in_inches
    if hasattr(root.Items.Item.ItemAttributes, 'ProductGroup'):
        if root.Items.Item.ItemAttributes.ProductGroup.text == 'Music':
            details['format'] = 'Sound Recording'
        elif root.Items.Item.ItemAttributes.ProductGroup.text == 'DVD':
            details['format'] = 'Video/Film'
        else:
            details['format'] = 'book'
    if hasattr(root.Items.Item.ItemAttributes, 'PublicationDate'):
        details['pub_date'] = get_year_from_raw_date(root.Items.Item.ItemAttributes.PublicationDate.text)

        
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
    details['format'] = 'Sound Recording'
    details['creator'] = name_element.text
    details['pub_date'] = get_year_from_raw_date(date_element.text)
    
    return details

def get_goodreads_details(url):
    """Given a goodreads URL, get title, creator, etc.
    """
    
    # Look for something like http://www.goodreads.com/book/show/40694.Ray_Bradbury_s_Fahrenheit_451

    details = {}
    
    #TODO: we should do some validation/error handling here
    url = url + '.xml'
    url_params = {'key' : GOODREADS['KEY']}
    data = urllib.urlencode(url_params)
    url = url + '?' + data
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    raw_response = response.read()

    root = objectify.fromstring(raw_response)
    
    details['format'] = 'book'
    
    if hasattr(root.book, 'title'):
        details['title'] = root.book.title
    if hasattr(root.book.authors.author, 'name'):
        details['creator'] = root.book.authors.author.name
    if hasattr(root.book.work, 'original_publication_year'):
        details['pub_date'] = get_year_from_raw_date(root.book.work.original_publication_year)
    if hasattr(root.book, 'isbn'):
        details['isbn'] = root.book.isbn
    if hasattr(root.book, 'num_pages') and len(root.book.num_pages.text) > 0:
        details['measurement_page_numeric'] = root.book.num_pages

    return details

def get_openlibrary_details(url):
    """Given an openlibrary URL, get title, creator, etc.
    """
    
    # Look for something like http://openlibrary.org/works/OL16501593W/Too_Big_to_Know
    # or http://openlibrary.org/books/OL24258898M/Rabbit_Run

    details = {}
    
    # Get the JSON representation of the web resource
    matches = re.search(r'(.*OL.*)\/', url)
    base_ol_url = matches.group(1)
    base_ol_url = base_ol_url + '.json'
        
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    to_open = opener.open(base_ol_url)
    response = to_open.read()

    serialized_response = json.loads(response)
    
    if 'title' in serialized_response:
        details['title'] = serialized_response['title']
        
    if 'publish_date' in serialized_response:
        details['pub_date'] = serialized_response['publish_date']

    if 'number_of_pages' in serialized_response:
        details['measurement_page_numeric'] = serialized_response['number_of_pages']
    elif 'pagination' in serialized_response:
        details['measurement_page_numeric'] = get_numeric_page_count(serialized_response['pagination'])
        
    if 'isbn_10' in serialized_response:
        details['isbn'] = serialized_response['isbn_10'][0]
    elif 'isbn_13' in serialized_response:
        details['isbn'] = serialized_response['isbn_13'][0]

    # TODO: Determine if this key in list business is the best approach. feels clunky.

    # The work/book returns the path to the author, get it here:
    if "key" in serialized_response["authors"][0]:
        authors_url_path =  serialized_response["authors"][0]["key"]
        
    elif "author" in serialized_response["authors"][0] and "key" in serialized_response["authors"][0]["author"]:
        authors_url_path =  serialized_response["authors"][0]["author"]["key"]
        
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    to_open = opener.open('http://openlibrary.org' + authors_url_path + '.json')
    response = to_open.read()

    serialized_response = json.loads(response)

    if 'name' in serialized_response:
        details['creator'] = serialized_response['name']

    return details

def get_web_resource(url):
    """Someone is trying to add a webpage to a shelf (or
     we can't figure out what they're trying to add"""
   
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    to_open = opener.open(url)
    response = to_open.read()
    
    # Use Beautiful Soup to create a workable object from the source
    soup = BeautifulSoup(response)
    
    title = soup.title.string

    parsed_url = urlparse(url)
    creator = parsed_url[1]

    details = {}
    
    details['format'] = 'webpage'
    
    if title:
        details['title'] = title
    if creator:
        details['creator'] = creator
    
    return details