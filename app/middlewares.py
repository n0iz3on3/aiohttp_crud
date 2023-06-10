import time
from typing import Awaitable, Callable
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


@middleware
async def session_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    async with Session() as session:
        request['session'] = session
        return await handler(request)


@middleware
async def check_auth_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    token = request.headers.get('token')
    if not token:
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
