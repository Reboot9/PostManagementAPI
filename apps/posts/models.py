from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models

from profanity_check import predict_prob

User = get_user_model()


class Post(models.Model):
    """
    Post model.
    """
    title = models.CharField(max_length=255)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)

    # Fields for automatic replies
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_delay = models.PositiveIntegerField(default=0, help_text="Auto delay for comment in seconds")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Check for profanity in title and content
        :param args:
        :param kwargs:
        :return:
        """
        if predict_prob([self.title])[0] > 0.5 or predict_prob([self.content])[0] > 0.5:
            self.is_blocked = True
        super().save(*args, **kwargs)
