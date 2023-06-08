import time
from typing import Awaitable, Callable
from bcrypt import hashpw, gensalt, checkpw
from aiohttp.web import (
    HTTPForbidden,
    HTTPNotFound,
    Request,
    StreamResponse,
    middleware,
)

from config import TOKEN_TTL
from crud import SQLAlchemyCRUD
from models import Session, Token
from errors import raise_http_error


def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()


def check_password(password_hash: str, password: str,) -> bool:
    return checkpw(password.encode(), password_hash.encode())


def is_owner(request: Request, user_id: int | None):
    if not request['token'] or request['token'].user.id != user_id:
        raise_http_error(HTTPForbidden, 'no rights to take action')


@middleware
async def session_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    async with Session() as session:
        request['session'] = session
        return await handler(request)


@middleware
def check_auth_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    try:
        token = request.headers.get('token')
    except (ValueError, TypeError):
        raise raise_http_error(HTTPForbidden, 'incorrect token')
    try:
        crud = SQLAlchemyCRUD(request['session'], Token)
        token = await crud.get_item(token)
    except HTTPNotFound:
        token = None

    if token is None:
        raise raise_http_error(HTTPForbidden, 'incorrect token')

    if time.time() - token.creation_time.timestamp() > TOKEN_TTL:
        raise raise_http_error(HTTPForbidden, 'incorrect token')

    request['token'] = token
    return await handler(request)
