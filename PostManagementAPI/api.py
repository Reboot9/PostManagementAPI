from ninja import NinjaAPI

from apps.users.api import router as users_router
from apps.posts.api import router as posts_router
from apps.comments.api import router as comments_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/posts/", posts_router)
api.add_router("/comments/", comments_router)