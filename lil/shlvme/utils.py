import datetime


def get_current_year():
    now = datetime.datetime.now()
    return str(now.year)

"""
def serialize_shelf(shelves):
    docs = []
    for shelf in shelves:
        doc = {}
        doc['shelf_uuid'] = str(shelf.shelf_uuid)
        doc['user_name'] = shelf.user.username
        doc['name'] = shelf.name
        doc['description'] = shelf.description
        doc['creation_date'] = shelf.creation_date
        doc['is_public'] = shelf.is_public
        
        list_of_items = []
        item_to_serialize = {}
        items = Item.objects.filter(shelf=shelves)
        for item in items:
            item_to_serialize['title'] = item.title
            item_to_serialize['creator'] = item.creator
            item_to_serialize['isbn'] = item.isbn
            item_to_serialize['web_location'] = item.web_location
            item_to_serialize['height'] = item.height
            item_to_serialize['width'] = item.width
            doc['shelfrank'] = item.shelfrank
            item_to_serialize['content_type'] = item.content_type
            item_to_serialize['creation_date'] = item.creation_date
            item_to_serialize['sort_order'] = item.sort_order
            
            list_of_items.append(item_to_serialize)
            
        doc['items'] = list_of_items
        docs.append(doc)
"""