import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, password_validation
from django.core.exceptions import ValidationError
from ninja import Router

from apps.users.schema import UserRegistrationSchema, UserOutSchema, ErrorSchema, UserLoginSchema, TokenSchema, \
    RefreshTokenSchema, AccessTokenSchema
from apps.users.utils import generate_access_token, generate_refresh_token

router = Router()

User = get_user_model()


@router.post("/register", response={201: UserOutSchema, 400: ErrorSchema})
def register_user(request, data_in: UserRegistrationSchema):
    if data_in.password1 != data_in.password2:
        return 400, {"message": "Passwords do not match"}
    try:
        # Validate passwords
        password_validation.validate_password(data_in.password1)

        # Create user instance
        user = User.objects.create_user(
            email=data_in.email,
            username=data_in.username,
            password=data_in.password1,
        )

        return 201, {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    except ValidationError as e:
        return 400, {"message": str(e)}


@router.post("/token", response={200: TokenSchema, 401: ErrorSchema})
def token(request, data_in: UserLoginSchema):
    """
    Authenticates users based on credentials (username and password) and issues JWT tokens
    """
    user = authenticate(username=data_in.username, password=data_in.password)
    if user is None:
        return 401, {"message": "Invalid credentials"}

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    return 200, {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/token/refresh", response={200: AccessTokenSchema, 401: ErrorSchema, 404: ErrorSchema})
def refresh_token(request, data_in: RefreshTokenSchema):
    # Extract the access token from the request data
    refresh_token = data_in.refresh_token

    try:
        # Decode and verify the refresh token
        payload = jwt.decode(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return 404, {"message": "User does not exist"}

        # Generate a new access token
        access_token = generate_access_token(user)

        return 200, {"access_token": access_token}
    except jwt.ExpiredSignatureError:
        return 401, {"message": "Refresh token has expired"}
    except jwt.InvalidTokenError:
        return 401, {"message": "Invalid refresh token"}
