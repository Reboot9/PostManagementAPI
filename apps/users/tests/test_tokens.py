import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from apps.users.api import router
from apps.users.utils import generate_refresh_token

User = get_user_model()


class TokenTests(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.register_url = "/register"
        self.token_url = "/token"
        self.refresh_url = "/token/refresh"

        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'passwordtest',
            'password2': 'passwordtest',
        }

        self.login_data = {
            'username': 'testuser',
            'password': 'passwordtest',
        }

        self.user = User.objects.create_user(email=self.user_data['email'], username=self.user_data['username'],
                                             password=self.user_data['password1'])

    def test_token_success(self):
        response = self.client.post(self.token_url, json=self.login_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())
        self.assertIn('refresh_token', response.json())

    def test_token_invalid_credentials(self):
        invalid_login_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.token_url, json=invalid_login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['message'], 'Invalid credentials')

    def test_refresh_token_success(self):
        # Generate a refresh token for the user
        refresh_token = generate_refresh_token(self.user)
        response = self.client.post(self.refresh_url, json={'refresh_token': refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())

    def test_refresh_token_expired(self):
        # Generate an expired refresh token for testing
        expired_refresh_token = jwt.encode({'user_id': self.user.id, 'exp': 0}, settings.REFRESH_TOKEN_SECRET_KEY,
                                           algorithm='HS256')
        response = self.client.post(self.refresh_url, json={'refresh_token': expired_refresh_token})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['message'], 'Refresh token has expired')

    def test_refresh_token_invalid(self):
        invalid_refresh_token = 'invalid_token_here'
        response = self.client.post(self.refresh_url, json={'refresh_token': invalid_refresh_token})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['message'], 'Invalid refresh token')

    def test_refresh_token_user_not_exist(self):
        # Generate a refresh token for a non-existent user
        invalid_user_refresh_token = jwt.encode({'user_id': 999999}, settings.REFRESH_TOKEN_SECRET_KEY,
                                                algorithm='HS256')
        response = self.client.post(self.refresh_url, json={'refresh_token': invalid_user_refresh_token})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'User does not exist')
