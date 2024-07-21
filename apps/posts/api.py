from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination

from PostManagementAPI.schemas.errors import ErrorSchema
from apps.comments.models import Comment
from apps.comments.schema import CommentOutSchema
from apps.posts.models import Post
from apps.posts.schema import PostOutSchema, PostInSchema
from apps.users.auth import JWTBearer

router = Router()

User = get_user_model()


@router.post("/", response={201: PostOutSchema, 500: ErrorSchema}, auth=JWTBearer())
def create_post(request, post_data: PostInSchema):
    """
    Create a new post
    :param request: request object
    :param post_data: post data
    :return: 201: If post was created successfully, 500: If any error occurs
    """
    author = request.auth

    try:
        # Create the post
        post = Post.objects.create(
            title=post_data.title,
            content=post_data.content,
            author=author,
        )

        return 201, post
    except Exception as e:
        return 500, {"message": str(e)}


@router.get("/", response={200: List[PostOutSchema]})
@paginate(PageNumberPagination)
def get_posts(request):
    """
    List all not blocked posts.
    :param request: request object.
    :return: 200: List of not blocked posts.
    """
    posts = Post.objects.filter(is_blocked=False)

    return posts


@router.get("/{pk}", response={200: PostOutSchema, 404: ErrorSchema})
def get_post(request, pk: int):
    """
    Retrieve a post by its pk.
    :param request: request object
    :param pk: post id
    :return: 200: If post was successfully retrieved, 404: If post was not found
    """
    try:
        post = get_object_or_404(Post, pk=pk, is_blocked=False)
        return 200, post
    except Post.DoesNotExist:
        return 404, {"message": "No Post matches the given query"}


@router.put("/{pk}", response={200: PostOutSchema, 403: ErrorSchema, 404: ErrorSchema}, auth=JWTBearer())
def update_post(request, pk: int, post_data: PostInSchema):
    """
    Update a post identified by its primary key (pk).
    :param request: request object
    :param pk: post id
    :param post_data: updated data for the post
    :return: 200: If the post was updated successfully, 403: If user doesn't have permission to update the post,
    404: If post was not found
    """
    try:
        post = get_object_or_404(Post, pk=pk, is_blocked=False)
    except Post.DoesNotExist:
        return 404, {"message": "No Post matches the given query"}
    user = request.auth

    # Check if the authenticated user is staff or the post's author
    if not user.is_staff or post.author != user:
        return 403, {"message": "You do not have permission to update this post"}

    for attr, value in post_data.dict().items():
        setattr(post, attr, value)

    post.save()

    return 200, post


@router.delete("/{pk}", response={204: None, 403: ErrorSchema, 404: ErrorSchema}, auth=JWTBearer())
def delete_post(request, pk: int):
    """
    Delete an existing post.
    :param request: request object
    :param pk: post id
    :return: 204 No Content: If the post is successfully deleted, 403: If user doesn't have permission to delete post,
    404: If post wasn't found
    """
    try:
        post = get_object_or_404(Post, pk=pk, is_blocked=False)
        user = request.auth

        # Check if the authenticated user is staff or the post's author
        if not user.is_staff or post.author != user:
            return 403, {"message": "You do not have permission to delete this post"}

        post.is_blocked = True
        post.save()
        return 204
    except Post.DoesNotExist:
        return 404, {"message": "No Post matches the given query"}


@router.get("/{post_id}/comments", response={200: List[CommentOutSchema], 404: ErrorSchema})
@paginate(PageNumberPagination)
def get_post_comments(request, post_id: int):
    """
    Retrieve all comments related to a post.

    :param request: request object
    :param post_id: primary key of the post to retrieve comments for

    :returns: 200: A list of comments related to the post.
    404: If no post matching the given post_id is found.
    """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post, is_blocked=False).select_related('author')

    return comments
