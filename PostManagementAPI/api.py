from ninja import NinjaAPI

from apps.users.api import router as users_router
from apps.posts.api import router as posts_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/posts/", posts_router)
