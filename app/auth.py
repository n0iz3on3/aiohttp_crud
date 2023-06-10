from aiohttp.web import Request, HTTPForbidden

from errors import raise_http_error
from bcrypt import hashpw, gensalt, checkpw


async def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()


async def check_password(password_hash: str, password: str,) -> bool:
    return checkpw(password.encode(), password_hash.encode())


async def check_owner(request: Request, user_id: int | None):
    if not request['token'] or request['token'].user.id != user_id:
        raise raise_http_error(HTTPForbidden, 'no rights to take action')
