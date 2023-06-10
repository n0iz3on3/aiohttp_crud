import re
import json

from typing import Optional, Callable
from aiohttp.web import Response, json_response
from pydantic.error_wrappers import ValidationError
from pydantic import BaseModel, EmailStr, Extra, validator

from config import PASSWORD_LENGTH


PASSWORD_REGEX = re.compile(
    '^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])*.{{{password_length},}}$'.format(
        password_length=PASSWORD_LENGTH
    )
)


class Register(BaseModel, extra=Extra.forbid):

    email: EmailStr
    password: str

    @classmethod
    @validator('password')
    def strong_password(cls, value: str):
        if not PASSWORD_REGEX.match(value):
            raise ValueError('password is to easy')
        return value


class Login(BaseModel, extra=Extra.forbid):

    email: EmailStr
    password: str


class PatchUser(BaseModel, extra=Extra.forbid):

    email: Optional[EmailStr]
    password: Optional[str]


class CreateAds(BaseModel, extra=Extra.forbid):

    title: str
    description: str

    @classmethod
    @validator('title')
    def validate_title(cls, value: str):
        if not (5 <= len(value) <= 35):
            raise ValueError('incorrect title length')
        return value

    @classmethod
    @validator('description')
    def validate_description(cls, value: str):
        if len(value) > 120:
            raise ValueError('description character limit exceeded')
        return value


class PatchAds(CreateAds, BaseModel, extra=Extra.forbid):

    title: Optional[str]
    description: Optional[str]


def validate(base_model) -> Callable:
    """Validate decorator."""
    def decorator(handler) -> Callable:
        async def wrapper(view) -> Response:
            json_data = await view.request.json()
            try:
                base_model(**json_data)
            except ValidationError as e:
                return json_response(
                    {'error': json.loads(e.json())}, status=400
                )
            return await handler(view)
        return wrapper
    return decorator
