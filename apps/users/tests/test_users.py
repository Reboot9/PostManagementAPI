from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from apps.users.api import router

User = get_user_model()


class UserTest(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.register_url = "/register"
        self.token_url = "/token"

    def test_user_registration(self):
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'passwordtest',
            'password2': 'passwordtest',
        }

        response = self.client.post(self.register_url, json=user_data)

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json())
        self.assertEqual(response.json()['username'], 'testuser')
