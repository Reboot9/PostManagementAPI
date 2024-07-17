import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer

User = get_user_model()


class JWTBearer(HttpBearer):
    """
    JWT Bearer Token Authentication for Django Ninja.
    """
    def authenticate(self, request, token):
        """
        Authenticates the user based on the provided JWT token.

        :param request: request object
        :param token: JWT token extracted from the request header.
        :return: User instance or None if the token is invalid.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                return None  # Return None if token is invalid

            # Check if user exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None  # Return None if user does not exist

            # Optionally, you can perform additional checks like token expiration here

            return user  # Return the user object if authentication succeeds

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None  # Return None if token is invalid or expired
