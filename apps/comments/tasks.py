from __future__ import absolute_import, unicode_literals
from celery import shared_task

from apps.comments.models import Comment


@shared_task
def auto_reply_to_comment(comment_id: int):
    try:
        comment = Comment.objects.get(pk=comment_id)
        post = comment.post
        user = post.author

        # Ensure auto-reply is enabled for the post
        if not post.auto_reply_enabled:
            return

        # Create a reply
        reply_text = f"Thank you for your comment on '{post.title}'! We appreciate your input."
        Comment.objects.create(
            text=reply_text,
            post=post,
            author=user,
            parent=comment,
        )
    except Comment.DoesNotExist:
        pass
