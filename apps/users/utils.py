from datetime import datetime, timedelta

import jwt
from django.conf import settings


def generate_access_token(user):
    access_token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(refresh_token_payload, settings.REFRESH_TOKEN_SECRET_KEY, algorithm='HS256')
