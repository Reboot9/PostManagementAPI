from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from apps.posts.models import Post  # Adjust the import according to your project structure
from apps.users.utils import generate_access_token
from apps.posts.api import router
from datetime import timedelta
import jwt
from django.conf import settings

User = get_user_model()


class PostTests(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.create_post_url = "/"
        self.get_posts_url = "/"
        self.get_post_url = "/{pk}"
        self.update_post_url = "/{pk}"
        self.delete_post_url = "/{pk}"
        self.get_post_comments_url = "/{post_id}/comments"

        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='password123')
        self.user1 = User.objects.create_user(email='test1@example.com', username='testuser1', password='password123')
        self.admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='password123')

        self.post_data = {
            'title': 'Test Post',
            'content': 'This is a test post content.',
            'auto_reply_enabled': False,
            'auto_reply_delay': 0,
        }

        self.post = Post.objects.create(
            title='Existing Post',
            content='Existing post content.',
            author=self.user,
            auto_reply_enabled=False,
            auto_reply_delay=0
        )

        self.auth_headers = {
            'Authorization': f'Bearer {generate_access_token(self.user)}'
        }
        self.auth1_headers = {
            'Authorization': f'Bearer {generate_access_token(self.user1)}'
        }
        self.admin_headers = {
            'Authorization': f'Bearer {generate_access_token(self.admin)}'
        }

    def test_create_post_success(self):
        response = self.client.post(self.create_post_url, json=self.post_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], self.post_data['title'])

    def test_get_posts(self):
        response = self.client.get(self.get_posts_url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)  # Check that there are posts returned

    def test_get_post_success(self):
        response = self.client.get(self.get_post_url.format(pk=self.post.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], self.post.title)

    def test_get_post_not_found(self):
        response = self.client.get(self.get_post_url.format(pk=9999))
        self.assertEqual(response.status_code, 404)

    def test_update_post_success(self):
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
        }
        response = self.client.put(self.update_post_url.format(pk=self.post.pk), json=updated_data,
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], updated_data['title'])

    def test_update_post_permission_denied(self):
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
        }
        response = self.client.put(self.update_post_url.format(pk=self.post.pk), json=updated_data,
                                   headers=self.auth1_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], 'You do not have permission to update this post')

    def test_update_post_not_found(self):
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
        }
        response = self.client.put(self.update_post_url.format(pk=9999), json=updated_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_post_success(self):
        response = self.client.delete(self.delete_post_url.format(pk=self.post.pk), headers=self.auth_headers)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(Post.objects.filter(pk=self.post.pk, is_blocked=True).exists())

    def test_delete_post_permission_denied(self):
        response = self.client.delete(self.delete_post_url.format(pk=self.post.pk), headers=self.auth1_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], 'You do not have permission to delete this post')

    def test_delete_post_not_found(self):
        response = self.client.delete(self.delete_post_url.format(pk=9999), headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_get_post_comments_success(self):
        response = self.client.get(self.get_post_comments_url.format(post_id=self.post.pk))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_get_post_comments_not_found(self):
        response = self.client.get(self.get_post_comments_url.format(post_id=9999))
        self.assertEqual(response.status_code, 404)

    def test_get_post_comments_no_comments(self):
        # Create a post with no comments
        post_without_comments = Post.objects.create(
            title='Post without comments',
            content='Content',
            author=self.user,
            auto_reply_enabled=False,
            auto_reply_delay=0
        )
        response = self.client.get(self.get_post_comments_url.format(post_id=post_without_comments.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['items'], [])
