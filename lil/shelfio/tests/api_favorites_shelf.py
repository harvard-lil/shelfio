import json

from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from lil.shelfio.models import Shelf, AuthTokens, FavoriteShelf 

class FavoritesShelfAPITestCase(unittest.TestCase):
    """Test the Shelf API
    """
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        
        # Create our first user
        self.client.post(reverse('process_register'), {'username': 'testuser1', 'email': 'testuser1@example.com', 'password': 'testpass'})
        self.client.login(username='testuser1', password='testpass')
        self.assertTrue('_auth_user_id' in self.client.session)

        # Get the user created in setup
        self.user_1 = User.objects.get(username='testuser1')

        # each user gets a shelf and an auth token at user creation time.
        self.misc_shelf_1 = Shelf.objects.get(user=self.user_1, name='Misc')
        self.auth_tokens_1 = AuthTokens.objects.get(user=self.user_1)

        # Create a our second user
        self.client.post(reverse('process_register'), {'username': 'testuser2', 'email': 'testuser2@example.com', 'password': 'testpass'})
        self.client.login(username='testuser2', password='testpass')
        self.assertTrue('_auth_user_id' in self.client.session)

        # Get the user created in setup
        self.user_2 = User.objects.get(username='testuser2')

        # each user gets a shelf and an auth token at user creation time.
        self.misc_shelf_2 = Shelf.objects.get(user=self.user_2, name='Misc')
        self.auth_tokens_2 = AuthTokens.objects.get(user=self.user_2)       

    def test_create_fav_shelf(self):
        """Create a favorite_shelf using the item api"""
                
        # user 1 favorites user 2's misc shelf
        self.client.post(reverse('favorites_api_shelves', kwargs={'user_name': self.user_1.username}), {'shelf_id': str(self.misc_shelf_2.shelf_uuid), 'access_token': str(self.auth_tokens_1.token)})

        user_1_favorites = FavoriteShelf.objects.get(user=self.user_1)
        
        # Does the favorite exist in the db??
        self.assertEqual(user_1_favorites.shelf, self.misc_shelf_2)
        
    def test_get_all_fav_shelves(self):
        """get all favorite shelves fro a user from the API"""
        
        # user 1 favorites user 2's misc shelf
        response = self.client.get(reverse('favorites_api_shelves', kwargs={'user_name': self.user_1.username}), {'access_token': str(self.auth_tokens_1.token)})

        user_1_favorites = FavoriteShelf.objects.get(user=self.user_1)
        
        shelf_from_get_api = json.loads(str(response.content))
        self.assertEqual(shelf_from_get_api['docs'][0]['name'], 'Misc')
        # Make sure we have some docs in the returned array. This is ugly.
        self.assertTrue(1 <= shelf_from_get_api['num'] <= 10)
        
    def test_get_one_fav_shelf(self):
        """get one favorite shelf using the item api"""
        
        # create a new shelf for user 2 so that user 1 can favorite it
        user_2_test_shelf= Shelf(user=self.user_2, name='Test shelf', description='a test shelf for the get fav shelf test')
        user_2_test_shelf.save()
        
        # user 1 favorites user 2's misc shelf
        response = self.client.post(reverse('favorites_api_shelves', kwargs={'user_name': self.user_1.username}), {'shelf_id': str(user_2_test_shelf.shelf_uuid), 'access_token': str(self.auth_tokens_1.token)})

        user_1_favorite_shelf= FavoriteShelf.objects.get(user=self.user_1, shelf=user_2_test_shelf)
        
        # Does the favorite exist in the db??
        self.assertEqual(user_1_favorite_shelf.shelf, user_2_test_shelf)

        # get our favorite
        response = self.client.get(reverse('favorites_api_shelf', kwargs={'user_name': self.user_1.username, 'favorite_shelf_uuid': response.content}), {'access_token': str(self.auth_tokens_1.token)})
        fav_shelf_from_get_api = json.loads(str(response.content))
        self.assertEqual(fav_shelf_from_get_api['docs'][0]['shelf_uuid'], str(user_2_test_shelf.shelf_uuid))

    def test_delete_fav_shelf(self):
        """Delete a favorite_shelf using the item api"""
        
        # create a new shelf for user 2 so that we can delete it
        user_2_test_shelf= Shelf(user=self.user_2, name='another Test shelf', description='another test shelf for the get fav shelf test')
        user_2_test_shelf.save()
        
        favorite_shelf = FavoriteShelf(user=self.user_1, shelf=user_2_test_shelf)
        favorite_shelf.save()
        
        # delete the test shelf through the api
        response = self.client.post(reverse('favorites_api_shelf', kwargs={'user_name': self.user_1.username, 'favorite_shelf_uuid': favorite_shelf.favorite_shelf_uuid}), {'_method': 'DELETE', 'access_token': str(self.auth_tokens_1.token)})
        
        deleted_favorite_shelf= FavoriteShelf.objects.filter(favorite_shelf_uuid=favorite_shelf.favorite_shelf_uuid)
        
        
        self.assertEqual(len(deleted_favorite_shelf), 0)
        self.assertEqual(204, response.status_code)