from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from lil.shlvme.models import Shelf, Item, Tag
from django.contrib.auth.models import User

@csrf_exempt
def api_tag(request, url_tag_uuid=None):
    """API for tags
    Something like shlv.me/api/tag/7838a693-7ea9-4f3a-8e4f-40ad3b8492e3
    TODO: we need to validate/clean/urldecode the GET/POST values
    """
    
    # Add a new tag to an item
    # TODO: All kinds of validation. Also, some type of transaction so that the item and creator are saved together?
    if request.method == 'POST' and request.user.is_authenticated():
        target_user = User.objects.get(username=request.user.username)
        target_item = Item.objects.get(item_uuid=request.POST.get('item-uuid'))
        target_shelf = Shelf.objects.get(shelf_uuid = target_item.shelf.shelf_uuid)
        
        if target_shelf.user == request.user:
            staged_tag = Tag(item=target_item, key=request.POST.get('tag-key'), value=request.POST.get('tag-value'))
            staged_tag.save()
            
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=401)
        
    else:
        return HttpResponse(status=401)
    
    # Delete an existing tag
    if request.method == 'DELETE' and request.user.is_authenticated() and url_tag_uuid is not None:
        # TODO Fix. This feels so wrong:
        target_tag = Tag.objects.get(tag_uuid = url_tag_uuid)
        target_item = Item.objects.get(item_uuid = target_tag.item.item_uuid)
        target_shelf = Shelf.objects.get(shelf_uuid = target_item.shelf.shelf_uuid)
        target_user = User.objects.get(username = target_shelf.user.username)
    
        # Get tags for item that user owns
        if request.user.is_authenticated():
            
            # User owns the shelf
            if target_shelf.user == target_user:
                target_tag.delete()
                return HttpResponse(status=202)
                
            else:
                return HttpResponse(status=401)

        
    # Edit an existing shelf
    elif request.method == 'POST' and request.user.is_authenticated() and url_tag_uuid is not None:
        return HttpResponse(status=202)

    # Get tags for an item
    elif request.method == 'GET' and request.user.is_authenticated() and url_tag_uuid is not None:
        pass
    
    # TODO: trap errors
    # try:
    #     p = Publisher.objects.get(name='Apress')
    # except Publisher.DoesNotExist:
    #    print "Apress isn't in the database yet."
    # else:
    #     print "Apress is in the database."