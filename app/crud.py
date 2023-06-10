from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp.web import HTTPForbidden, HTTPNotFound

from errors import raise_http_error
from models import ORM_MODEL, ORM_MODEL_CLS


class SQLAlchemyCRUD:
    def __init__(self, session: AsyncSession, model: ORM_MODEL | ORM_MODEL_CLS) -> None:
        self.model = model
        self.session = session

    async def get_item(self, item_id: int | str) -> ORM_MODEL:
        item = await self.session.get(self.model, item_id)
        if item is None:
            raise raise_http_error(HTTPNotFound, f'{self.model.__name__.lower()} not found')
        return item

    async def create_item(self, item: ORM_MODEL):
        self.session.add(item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(HTTPForbidden, f'such {self.model.__name__.lower()} already exists')

    async def patch_item(self, params_json, item_id: int | str):
        item = await self.get_item(item_id)
        for field, value in params_json.items():
            setattr(item, field, value)
        self.session.add(item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(HTTPForbidden, f'attr already exists')

    async def delete_item(self, item_id):
        item = await self.get_item(item_id)
        if item is None:
            raise raise_http_error(HTTPNotFound, f'no item was found')
        await self.session.delete(item)
        await self.session.commit()
