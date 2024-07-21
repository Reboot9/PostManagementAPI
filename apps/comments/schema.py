from datetime import datetime, date
from typing import List, Optional

from ninja import Schema


class ReplySchema(Schema):
    id: int
    text: str
    author_id: int
    created_at: datetime


class CommentInSchema(Schema):
    text: str
    # optional because it's required only when creating comment, not updating
    post_id: int = None


class CommentOutSchema(Schema):
    id: int
    text: str
    author_id: int
    replies: List[ReplySchema] = []
    created_at: datetime


class CommentAnalyticsSchema(Schema):
    date: date
    total_comments: int
    blocked_comments: int
