from ninja import NinjaAPI, Schema
from pydantic import EmailStr


class UserRegistrationSchema(Schema):
    email: EmailStr
    username: str
    password1: str
    password2: str


class UserLoginSchema(Schema):
    username: str
    password: str


class UserOutSchema(Schema):
    id: int
    username: str
    email: EmailStr


class TokenSchema(Schema):
    access_token: str
    refresh_token: str


class RefreshTokenSchema(Schema):
    refresh_token: str


class AccessTokenSchema(Schema):
    access_token: str


class ErrorSchema(Schema):
    message: str
