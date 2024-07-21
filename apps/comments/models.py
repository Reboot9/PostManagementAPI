from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from profanity_check import predict_prob

from apps.posts.models import Post

User = get_user_model()


class Comment(models.Model):
    """
    Comment model.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f"{self.author} - {self.post}"

    def save(self, *args, **kwargs):
        """
        Override save method to check for profanity before saving to database.
        :param args: additional arguments
        :param kwargs: additional keyword arguments
        :return:
        """
        if predict_prob([self.text])[0] > 0.5:
            self.is_blocked = True

        super().save(*args, **kwargs)
