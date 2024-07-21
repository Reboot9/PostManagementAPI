from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import Router

from PostManagementAPI.schemas.errors import ErrorSchema
from apps.comments.models import Comment
from apps.comments.schema import CommentInSchema, CommentOutSchema, ReplySchema, CommentAnalyticsSchema
from apps.posts.models import Post
from apps.users.auth import JWTBearer

router = Router()

User = get_user_model()


@router.get("/comments-daily-breakdown", response={200: List[CommentAnalyticsSchema], 400: ErrorSchema})
def daily_breakdown(request, date_from: str, date_to: str):
    """
    Get daily breakdown of comments created and blocked within a date range.
    :param request: request object
    :param date_from: start date in YYYY-MM-DD format
    :param date_to: end date in YYYY-MM-DD format
    :return: list of daily breakdown data
    """
    if date_from > date_to:
        return 400, {"message": "date_from must be earlier than date_to"}

    daily_comments = Comment.objects.filter(
        created_at__date__gte=date_from, created_at__date__lte=date_to
    ).values('created_at__date').annotate(
        total_comments=Count('id'),
        blocked_comments=Count('id', filter=Q(is_blocked=True))
    ).order_by('created_at__date')

    # Convert to schema format
    result = [
        CommentAnalyticsSchema(
            date=item['created_at__date'],
            total_comments=item['total_comments'],
            blocked_comments=item['blocked_comments']
        ) for item in daily_comments
    ]

    return 200, result


@router.post("/",
             response={201: CommentOutSchema, 400: ErrorSchema, 404: ErrorSchema, 500: ErrorSchema},
             auth=JWTBearer())
def create_comment(request, comment_data: CommentInSchema):
    from apps.comments.tasks import auto_reply_to_comment
    if not comment_data.post_id:
        return 400, {"message": "post_id is required when creating comment"}
    try:
        post = get_object_or_404(Post, pk=comment_data.post_id, is_blocked=False)
        user = request.auth
    except Post.DoesNotExist:
        return 404, {"message": "Post does not exist"}

    try:
        comment = Comment.objects.create(
            text=comment_data.text,
            post=post,
            author=user,
        )

        # Schedule auto-reply if enabled
        if post.auto_reply_enabled and post.auto_reply_delay > 0:
            auto_reply_to_comment.apply_async(
                (comment.id,),
                countdown=post.auto_reply_delay
            )

        return 201, comment
    except Exception as e:
        return 500, {"message": str(e)}


@router.post("/{pk}/reply",
             response={201: ReplySchema, 400: ErrorSchema, 404: ErrorSchema},
             auth=JWTBearer())
def reply_to_comment(request, pk: int, reply_data: CommentInSchema):
    """
    Reply to a comment
    :param request: request object
    :param pk: primary key of the comment to reply to
    :param reply_data: comment data
    :return:
    """
    try:
        parent_comment = get_object_or_404(Comment, pk=pk, is_blocked=False)
        user = request.auth
    except Comment.DoesNotExist:
        return 404, {"message": "Comment does not exist"}

    # Create the reply
    reply = Comment.objects.create(
        text=reply_data.text,
        post=parent_comment.post,
        author=user,
        parent=parent_comment,
    )

    return 201, reply


@router.get("/{pk}", response={200: CommentOutSchema, 404: ErrorSchema})
def get_comment(request, pk: int):
    """
    Retrieve a comment and its replies
    :param request: request object
    :param pk: primary key of the comment to retrieve
    :return: comment and its replies
    """
    try:
        comment = get_object_or_404(Comment, pk=pk, is_blocked=False)
        return 200, comment
    except Comment.DoesNotExist:
        return 404, {"message": "Comment does not exist"}


@router.put("/{pk}", response={200: CommentOutSchema, 403: ErrorSchema, 404: ErrorSchema}, auth=JWTBearer())
def update_comment(request, pk: int, comment_data: CommentInSchema):
    """
    Update a comment
    :param request: request object
    :param pk: primary key of the comment to update
    :param comment_data: data to update
    :return: 200 if comment was updated, 403 if user does not have permission to update comment,
    404 if comment does not exist
    """
    user = request.auth
    comment = get_object_or_404(Comment, pk=pk, is_blocked=False)

    if comment.author != user and not user.is_staff:
        return 403, {"message": "You do not have permission to edit this comment"}

    comment.text = comment_data.text
    comment.save()

    return comment


@router.delete("/{pk}", response={204: None, 403: ErrorSchema, 404: ErrorSchema}, auth=JWTBearer())
def delete_comment(request, pk: int):
    """
    Delete an existing comment
    :param request: request object
    :param pk: primary key of the comment to delete
    :return: 204 if comment deleted successfully, 403 if user does not have permission to delete comment,
    404 if comment does not exist
    """
    comment = get_object_or_404(Comment, pk=pk, is_blocked=False)
    user = request.auth

    # Check if the authenticated user is staff or the comment's author
    if comment.author != user and not user.is_staff:
        return 403, {"message": "You do not have permission to delete this comment"}

    comment.is_blocked = True
    comment.save()
    return 204, None
