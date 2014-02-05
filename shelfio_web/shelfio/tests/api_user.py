import json

from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from lil.shelfio.models import Shelf, AuthTokens 

class UserAPITestCase(unittest.TestCase):
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

    def test_get_user(self):
        """Create a shelf using the item api"""
        
        # get a shelf
        response = self.client.get(reverse('api_user', kwargs={'url_user_name': self.user.username}),)

        user_from_get_api = json.loads(str(response.content))
        self.assertFalse('email' in user_from_get_api)
        
        # get a shelf
        response = self.client.get(reverse('api_user', kwargs={'url_user_name': self.user.username}), {'access_token': self.auth_tokens.token})

        user_from_get_api = json.loads(str(response.content))
        self.assertEqual(user_from_get_api['email'], self.user.email)
        
    def test_patch_item(self):
        """Update one field in an existing user (PATCH)"""
                
        self.client.post(reverse('api_user', kwargs={'url_user_name': self.user.username}), {'_method': 'PATCH', 'first_name': 'ben', 'access_token': self.auth_tokens.token})
        
        new_user = User.objects.get(username=self.user.username)
        
        self.assertEqual(new_user.email, 'testuser@example.com')
        self.assertEqual(new_user.first_name, 'ben')