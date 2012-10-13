import json

from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from lil.shelfio.models import Shelf, Item, AuthTokens 

class ItemAPITestCase(unittest.TestCase):
    """Test the Item API
    """
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
        # Create a user
        self.client.post(reverse('process_register'), {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpass'})
        self.client.login(username='testuser', password='testpass')
        self.assertTrue('_auth_user_id' in self.client.session)

        # Get the user created in setup
        self.user = User.objects.get(username='testuser')
        
        # each user gets a shelf and an auth token at user creation time.
        self.misc_shelf = Shelf.objects.get(user=self.user, name='Misc')
        self.auth_tokens = AuthTokens.objects.get(user=self.user)

    def tearDown(self):
        pass

    def test_post_item(self):
        """Create an item using the item api"""
        # create an item
        response = self.client.post(reverse('api_item_create'), {'shelf_uuid': self.misc_shelf.shelf_uuid, 'title': 'hey ma, it\'s a book', 'link': 'http://example.com', 'access_token': self.auth_tokens.token})
        
        # if all we went well, we should get the uuid of the created item
        item_uuid = response.content

        item = Item.objects.get(item_uuid=item_uuid)
        
        # Does the item returned equal the one in the db?
        self.assertEqual(str(item_uuid), str(item.item_uuid))

    def test_get_item(self):
        """Get an item using the item api"""

        item = Item(shelf=self.misc_shelf, title='get item test title', link='http://example.com',)
        item.save()
        
        response = self.client.get(reverse('api_item_by_uuid', kwargs={'url_item_uuid': item.item_uuid}))
        item_from_get_api = json.loads(str(response.content))
        self.assertEqual(item_from_get_api['title'], 'get item test title')
        
    def test_put_item(self):
        """Update an existing item (PUT)"""
        
        item = Item(shelf=self.misc_shelf, title='update item test title', link='http://example.com',)
        item.save()
                
        self.client.post(reverse('api_item_by_uuid', kwargs={'url_item_uuid': item.item_uuid}), {'_method': 'PUT', 'shelf_uuid': self.misc_shelf.shelf_uuid, 'title': 'hey ma, it\'s a different book', 'link': 'http://example.com', 'access_token': self.auth_tokens.token})

        new_item = Item.objects.get(item_uuid=item.item_uuid)
        
        self.assertEqual(new_item.title, 'hey ma, it\'s a different book')
        
    def test_patch_item(self):
        """Update one field in an existing item (PATCH)"""
        
        item = Item(shelf=self.misc_shelf, title='patch item test title', link='http://patch.example.com',)
        item.save()
                
        self.client.post(reverse('api_item_by_uuid', kwargs={'url_item_uuid': item.item_uuid}), {'_method': 'PATCH', 'link': 'http://new.patch.link.example.com', 'access_token': self.auth_tokens.token})

        new_item = Item.objects.get(item_uuid=item.item_uuid)
        
        self.assertEqual(new_item.link, 'http://new.patch.link.example.com')
        self.assertEqual(new_item.title, 'patch item test title')
        
    def test_delete_item(self):
        """Delete an existing item (DELETE)"""
    
        item = Item(shelf=self.misc_shelf, title='title for delete item test', link='http://example.com',)
        item.save()
        
        # Try to delete without our auth token. We shouldn't be able to        
        response = self.client.post(reverse('api_item_by_uuid', kwargs={'url_item_uuid': item.item_uuid}), {'_method': 'DELETE'})
        items = Item.objects.filter(item_uuid=item.item_uuid)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(404, response.status_code)
        
        # Delete with our auth token
        response = self.client.post(reverse('api_item_by_uuid', kwargs={'url_item_uuid': item.item_uuid}), {'_method': 'DELETE', 'access_token': self.auth_tokens.token})
        items = Item.objects.filter(item_uuid=item.item_uuid)
        
        self.assertEqual(len(items), 0)
        self.assertEqual(204, response.status_code)