import random
import json
import logging

from lil.shelfio.views.shelf import serialize_shelf
from lil.shelfio.models import Shelf

from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


def get_shelf():
    """get a random shelf. 
    """
    
    num_public_shelves = Shelf.objects.annotate(num_items=Count('item')).filter(is_private=False).filter(num_items__gt=1).count()
    random_shelf = Shelf.objects.annotate(num_items=Count('item')).filter(is_private=False).filter(num_items__gt=1)[random.randint(0, num_public_shelves - 1)]

    return random_shelf

@csrf_exempt    
def api_shelf(reqeust):
    """API to get a random shelf.
    """
    random_shelf = get_shelf();

    serialized_shelf = serialize_shelf(random_shelf)
    return HttpResponse(
        json.dumps(serialized_shelf, cls=DjangoJSONEncoder),
        mimetype='application/json',
    )