from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.comments.tasks import auto_reply_to_comment

from unittest.mock import patch
import json
from apps.comments.api import router
from datetime import datetime, timedelta

from apps.users.utils import generate_access_token

User = get_user_model()


class CommentTests(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.create_comment_url = "/"
        self.reply_comment_url = "/{pk}/reply"
        self.get_comment_url = "/{pk}"
        self.update_comment_url = "/{pk}"
        self.delete_comment_url = "/{pk}"
        self.daily_breakdown_url = "/comments-daily-breakdown"

        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='password123')
        self.user1 = User.objects.create_user(email='test1@example.com', username='testuser1', password='password123')
        self.admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='password123')

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=self.user,
            auto_reply_enabled=False,
            auto_reply_delay=0
        )

        self.comment = Comment.objects.create(
            text='Test comment content',
            post=self.post,
            author=self.user
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

    def test_daily_breakdown_success(self):
        today = datetime.now().date()
        past_date = today - timedelta(days=1)
        response = self.client.get(
            f"{self.daily_breakdown_url}?date_from={past_date}&date_to={today}",
            headers=self.auth_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)  # Ensure breakdown data is returned

    def test_daily_breakdown_date_order(self):
        today = datetime.now().date()
        response = self.client.get(
            f"{self.daily_breakdown_url}?date_from={today}&date_to={today - timedelta(days=1)}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'date_from must be earlier than date_to')

    def test_create_comment_success(self):
        comment_data = {
            'text': 'This is a new comment',
            'post_id': self.post.pk
        }
        response = self.client.post(self.create_comment_url, json=comment_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['text'], comment_data['text'])

    def test_create_comment_missing_post_id(self):
        comment_data = {
            'text': 'This comment has no post_id'
        }
        response = self.client.post(self.create_comment_url, json=comment_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'post_id is required when creating comment')

    def test_create_comment_post_not_found(self):
        comment_data = {
            'text': 'Comment for a non-existent post',
            'post_id': 9999
        }
        response = self.client.post(self.create_comment_url, json=comment_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_reply_to_comment_success(self):
        reply_data = {
            'text': 'This is a reply',
            'post_id': self.post.pk
        }
        response = self.client.post(self.reply_comment_url.format(pk=self.comment.pk), json=reply_data,
                                    headers=self.auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['text'], reply_data['text'])

    def test_reply_to_comment_not_found(self):
        reply_data = {
            'text': 'Reply to a non-existent comment',
            'post_id': self.post.pk
        }
        response = self.client.post(self.reply_comment_url.format(pk=9999), json=reply_data, headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_get_comment_success(self):
        response = self.client.get(self.get_comment_url.format(pk=self.comment.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['text'], self.comment.text)

    def test_get_comment_not_found(self):
        response = self.client.get(self.get_comment_url.format(pk=9999))
        self.assertEqual(response.status_code, 404)

    def test_update_comment_success(self):
        updated_data = {
            'text': 'Updated comment text'
        }
        response = self.client.put(self.update_comment_url.format(pk=self.comment.pk), json=updated_data,
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['text'], updated_data['text'])

    def test_update_comment_permission_denied(self):
        updated_data = {
            'text': 'Updated comment text'
        }
        response = self.client.put(self.update_comment_url.format(pk=self.comment.pk), json=updated_data,
                                   headers=self.auth1_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], 'You do not have permission to edit this comment')

    def test_update_comment_not_found(self):
        updated_data = {
            'text': 'Updated comment text'
        }
        response = self.client.put(self.update_comment_url.format(pk=9999), json=updated_data,
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_success(self):
        response = self.client.delete(self.delete_comment_url.format(pk=self.comment.pk), headers=self.auth_headers)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk, is_blocked=True).exists())

    def test_delete_comment_permission_denied(self):
        response = self.client.delete(self.delete_comment_url.format(pk=self.comment.pk), headers=self.auth1_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], 'You do not have permission to delete this comment')

    def test_delete_comment_not_found(self):
        response = self.client.delete(self.delete_comment_url.format(pk=9999), headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)
