"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import json

from django.test import TestCase
from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from lil.shelfio.models import Shelf, Item, Creator, AuthTokens 

"""
class MacroTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
        # Create a user
        self.client.post(reverse('process_register'), {'username': 'testuser', 'password1': 'testpass', 'password2': 'testpass'})
        self.client.login(username='testuser', password='testpass')
        self.assertTrue('_auth_user_id' in self.client.session)
        
    def tearDown(self):
        pass

    def test_create_shelf_and_populate(self):
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Create a shelf
        response = self.client.post(reverse('api_shelf'), {'shelf-name': 'test-shelf', 'description': 'this is my test shelf', 'is-public': True})
        self.assertEqual(response.status_code, 201)
        
        shelf = Shelf.objects.get()
        self.assertEqual('test-shelf', shelf.name)
        
        # Add an item to the shelf
        response = self.client.post(reverse('api_item'), {'shelf-name': 'test-shelf', 'title': 'test-title', 'creator': 'test-creator', 'isbn': 'test-isbn'})
        self.assertEqual(response.status_code, 201)
        
        item = Item.objects.get()
        self.assertEqual('test-title', item.title)
        
        
class ImdbTestCase(unittest.TestCase):
    #Test our IMDB bookmarklet functionality. We'll depend on the MacroTestCase to
    #set things up properly.
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
    def tearDown(self):
        pass

    def test_add_imdb_item(self):
        response = self.client.get(('%s?loc=http://www.imdb.com/title/tt0109686/' % reverse('incoming')))
        self.assertEqual('Dumb & Dumber', response.context['title'])

class AmazonTestCase(unittest.TestCase):
    #Test our Amazon bookmarklet functionality. We'll depend on the MacroTestCase to
    #set things up properly.
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
    def tearDown(self):
        pass

    def test_add_imdb_item(self):
        response = self.client.get(('%s?loc=http://www.amazon.com/Blood-Meridian-Evening-Redness-West/dp/0679728759/ref=sr_1_1?s=books&ie=UTF8&qid=1332896433&sr=1-1' % reverse('incoming')))
        self.assertEqual('Blood Meridian: Or the Evening Redness in the West', response.context['title'])
        
class MusicbrainzTestCase(unittest.TestCase):
    #Test our Musicbrainz bookmarklet functionality. We'll depend on the MacroTestCase to
    #set things up properly.
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.client.login(username='testuser', password='testpass')
        
    def tearDown(self):
        pass

    def test_add_mb_item(self):
        response = self.client.get(('%s?loc=http://musicbrainz.org/release-group/20e845b1-c6b5-44f7-ab7e-cbc0e33767b5' % reverse('incoming')), follow=True)
        self.assertEqual('1996', response.context['pub_date'])
        
"""     
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
        self.misc_shelf = Shelf.objects.get(user=self.user)
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
        self.assertTrue(str(item_uuid), item.item_uuid)

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
        