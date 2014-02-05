import json

from django.utils import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from shelfio.models import Shelf, AuthTokens, FavoriteUser

class FavoritesUserAPITestCase(unittest.TestCase):
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
        
        # Create a our third user
        self.client.post(reverse('process_register'), {'username': 'testuser3', 'email': 'testuser3@example.com', 'password': 'testpass'})
        # Get the user created in setup
        self.user_3 = User.objects.get(username='testuser3')
       

    def test_create_fav_user(self):
        """Create a favorite_user using the item api"""
        
        # user 1 favorites user 2
        self.client.post(reverse('favorites_api_users', kwargs={'user_name': self.user_1.username}), {'user_name': str(self.user_2.username), 'access_token': str(self.auth_tokens_1.token)})

        user_1_favorite_users = FavoriteUser.objects.get(follower=self.user_1)
        
        # Does the favorite exist in the db?
        self.assertEqual(user_1_favorite_users.leader, self.user_2)
        
    def test_get_all_fav_users(self):
        """get all favorite users for a user from the API"""
        
        # user 1 favorites user 3
        self.client.post(reverse('favorites_api_users', kwargs={'user_name': self.user_1.username}), {'user_name': str(self.user_3.username), 'access_token': str(self.auth_tokens_1.token)})
        
        # user 1 gets his/her favorite users
        response = self.client.get(reverse('favorites_api_users', kwargs={'user_name': self.user_1.username}), {'access_token': str(self.auth_tokens_1.token)})
        
        user_1_favorite_users = FavoriteUser.objects.filter(follower=self.user_1)
        
        favorite_users_from_get_api = json.loads(str(response.content))
        # Make sure we have some docs in the returned array. This is ugly.
        self.assertTrue(1 <= favorite_users_from_get_api['num'] <= 10)
        
        
    def test_get_one_fav_user(self):
        """get one favorite user using the item api"""
        
        # create a new user user 1 can favorite it
        self.client.post(reverse('process_register'), {'username': 'testuser4', 'email': 'testuser4@example.com', 'password': 'testpass'})
        # Get the user created in setup
        user_4 = User.objects.get(username='testuser4')
        
        # user 1 favorites user 2's misc shelf
        response = self.client.post(reverse('favorites_api_users', kwargs={'user_name': self.user_1.username}), {'user_name': user_4.username, 'access_token': str(self.auth_tokens_1.token)})

        # get our favorite
        response = self.client.get(reverse('favorites_api_user', kwargs={'user_name': self.user_1.username, 'favorite_user_uuid': response.content}), {'access_token': str(self.auth_tokens_1.token)})
        fav_user_from_get_api = json.loads(str(response.content))        
        self.assertEqual(fav_user_from_get_api['docs'][0]['user_name'], str(user_4.username))

    def test_delete_fav_user(self):
        """Delete a favorite_user using the item api"""
        
        # create a new user user 1 so that we can favorite the user
        self.client.post(reverse('process_register'), {'username': 'testuser5', 'email': 'testuser5@example.com', 'password': 'testpass'})
        # Get the user created in setup
        user_5 = User.objects.get(username='testuser5')
        
        favorite_user = FavoriteUser(leader=user_5, follower=self.user_1)
        favorite_user.save()
        
        # delete the test shelf through the api
        response = self.client.post(reverse('favorites_api_user', kwargs={'user_name': self.user_1.username, 'favorite_user_uuid': favorite_user.favorite_user_uuid}), {'_method': 'DELETE', 'access_token': str(self.auth_tokens_1.token)})
        
        deleted_favorite_user = FavoriteUser.objects.filter(favorite_user_uuid=favorite_user.favorite_user_uuid)
        
        self.assertEqual(len(deleted_favorite_user), 0)
        self.assertEqual(204, response.status_code)