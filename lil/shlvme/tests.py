"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from lil.shlvme.models import Shelf, Item, Creator, Tag 

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
        
        # Add a tag to the item
        response = self.client.post(reverse('api_tag'), {'item-uuid': item.item_uuid, 'tag-key': 'test-tag-key', 'tag-value': 'test-tag-value'})
        
        
class ImdbTestCase(unittest.TestCase):
    """Test our IMDB bookmarklet functionality. We'll depend on the MacroTestCase to
    set things up properly.
    """
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
    def tearDown(self):
        pass

    def test_add_imdb_item(self):
        response = self.client.get(('%s?loc=http://www.imdb.com/title/tt0109686/' % reverse('incoming')))
        self.assertEqual('Dumb & Dumber', response.context['title'])

class AmazonTestCase(unittest.TestCase):
    """Test our Amazon bookmarklet functionality. We'll depend on the MacroTestCase to
    set things up properly.
    """
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
    def tearDown(self):
        pass

    def test_add_imdb_item(self):
        response = self.client.get(('%s?loc=http://www.amazon.com/Blood-Meridian-Evening-Redness-West/dp/0679728759/ref=sr_1_1?s=books&ie=UTF8&qid=1332896433&sr=1-1' % reverse('incoming')))
        self.assertEqual('Blood Meridian: Or the Evening Redness in the West', response.context['title'])