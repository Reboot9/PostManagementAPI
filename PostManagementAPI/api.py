from ninja import NinjaAPI

from apps.users.api import router as users_router

api = NinjaAPI()

api.add_router("/users/", users_router),
