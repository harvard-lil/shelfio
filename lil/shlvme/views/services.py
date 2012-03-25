from django.shortcuts import render_to_response
from amazonproduct import API

def incoming(request):
    """We have an incoming item (probably from the bookmarklet)"""
    
    #TODO: this is nothing more than a test now. cleanup.
    url = request.GET.get('loc', None)
    matches = re.search(r'\/([A-Z0-9]{10})($|\/)', url)
    asin = matches.group(1)
    
    aws_key = AMZ.KEY 
    aws_secret_key = AMZ.SECRET_KEY 
    api = API(aws_key, aws_secret_key, 'us')
    
    for root in api.item_lookup(asin, IdType='ASIN', AssociateTag= AMZ.ASSOCIATE_TAG):
        nspace = root.nsmap.get(None, '')
        amazon_items = root.xpath('//aws:Items/aws:Item', namespaces={'aws' : nspace})
        author = u'Unknown'
        title = u'Unknown'
        isbn = u'Unknown'

        for amazon_item in amazon_items:
            if hasattr(amazon_item.ItemAttributes, 'Author'): 
                author = unicode(amazon_item.ItemAttributes.Author)

            if hasattr(amazon_item.ItemAttributes, 'Title'): 
                title = unicode(amazon_item.ItemAttributes.Title)
    
    return render_to_response('add-item.html', {'user': request.user, 'creator': author, 'title': title, 'isbn': isbn})