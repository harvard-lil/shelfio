import csv
import logging

from lil.shelfio.models import Item, Shelf

from django.shortcuts import get_object_or_404, HttpResponse
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


def export_shelf_as_csv(reqeust, shelf_uuid):
    """Receive a shelf uuid, return a csv of the serialized shelf
    """

    shelf = get_object_or_404(Shelf, shelf_uuid=shelf_uuid)

    # Let's require the user to be logged in and own the shelf in order to export it. Is this a good policy?
    if shelf.user != reqeust.user:
        return HttpResponse('Unauthorized. You must be logged in and must own the shelf to export.', status=401)

    items = Item.objects.filter(shelf=shelf)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=shelfio-shelf.csv'

    writer = csv.writer(response)
    
    # Write our header and then our values
    writer.writerow(model_to_dict(items[0]).keys())
    for item in items:
        writer.writerow(model_to_dict(item).values())

    return response