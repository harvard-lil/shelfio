import json

from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from lil.shelfio.models import Shelf, AuthTokens 

class ShelfAPITestCase(unittest.TestCase):
    """Test the Shelf API
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

    def test_post_shelf(self):
        """Create a shelf using the item api"""
        
        # create an shelf
        response = self.client.post(reverse('api_shelf_create'), {'name': 'I created this shelf through the api', 'description': 'some desc', 'access_token': self.auth_tokens.token})
        
        # if all we went well, we should get the uuid of the created item
        shelf_uuid = response.content

        shelf = Shelf.objects.get(shelf_uuid=shelf_uuid)
        
        # Does the item returned equal the one in the db?
        self.assertEqual(str(shelf_uuid), str(shelf.shelf_uuid))
        self.assertEqual('I created this shelf through the api', shelf.name)
        
    def test_get_shelf(self):
        """Get a shelf using the shelf api"""

        shelf = Shelf(user=self.user, name='test get shelf', description='some test get shelf desc',)
        shelf.save()
        
        response = self.client.get(reverse('api_shelf_by_uuid', kwargs={'url_shelf_uuid': shelf.shelf_uuid}))
        shelf_from_get_api = json.loads(str(response.content))
        self.assertEqual(shelf_from_get_api['name'], 'test get shelf')
        
        
    def test_delete_item(self):
        """Delete an existing shelf (DELETE)"""
    
        shelf = Shelf(user=self.user, name='test delete shelf', description='some test delete shelf desc',)
        shelf.save()
        
        # Try to delete without our auth token. We shouldn't be able to        
        response = self.client.post(reverse('api_shelf_by_uuid', kwargs={'url_shelf_uuid': shelf.shelf_uuid}), {'_method': 'DELETE'})
        shelves = Shelf.objects.filter(shelf_uuid=shelf.shelf_uuid)
                
        self.assertEqual(len(shelves), 1)
        self.assertEqual(404, response.status_code)
        
        # Delete with our auth token
        response = self.client.post(reverse('api_shelf_by_uuid', kwargs={'url_shelf_uuid': shelf.shelf_uuid}), {'_method': 'DELETE', 'access_token': self.auth_tokens.token})
        shelves = Shelf.objects.filter(shelf_uuid=shelf.shelf_uuid)

        self.assertEqual(len(shelves), 0)
        self.assertEqual(204, response.status_code)
        
    def test_put_shelf(self):
        """Update an existing shelf (PUT)"""
        
        shelf = Shelf(user=self.user, name='test put shelf', description='some test put shelf desc',)
        shelf.save()
                
        self.client.post(reverse('api_shelf_by_uuid', kwargs={'url_shelf_uuid': shelf.shelf_uuid}), {'_method': 'PUT', 'name': 'I updated this shelf through the api', 'description': 'some updated desc', 'access_token': self.auth_tokens.token})

        new_shelf = Shelf.objects.get(shelf_uuid=shelf.shelf_uuid)
        
        self.assertEqual(new_shelf.name, 'I updated this shelf through the api')

    def test_patch_item(self):
        """Update one field in an existing shelf (PATCH)"""
        
        shelf = Shelf(user=self.user, name='test patch shelf', description='some patch put shelf desc',)
        shelf.save()
                
        self.client.post(reverse('api_shelf_by_uuid', kwargs={'url_shelf_uuid': shelf.shelf_uuid}), {'_method': 'PATCH', 'description': 'whoa, different description', 'access_token': self.auth_tokens.token})
        
        new_shelf = Shelf.objects.get(shelf_uuid=shelf.shelf_uuid)
        
        self.assertEqual(new_shelf.description, 'whoa, different description')
        self.assertEqual(new_shelf.name, 'test patch shelf')
