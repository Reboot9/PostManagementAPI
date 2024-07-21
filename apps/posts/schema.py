from datetime import datetime

from ninja import Schema


class PostInSchema(Schema):
    title: str
    content: str
    auto_reply_enabled: bool = False
    auto_reply_delay: int = 0


class PostOutSchema(Schema):
    id: int
    title: str
    content: str
    author_id: int
    is_blocked: bool
    created_at: datetime
