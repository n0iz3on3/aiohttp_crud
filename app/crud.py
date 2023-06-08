from aiohttp.web import HTTPForbidden, HTTPNotFound
from errors import raise_http_error
from models import ORM_MODEL, ORM_MODEL_CLS
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyCRUD:
    def __int__(self, session: AsyncSession, model_cls: ORM_MODEL | ORM_MODEL_CLS):
        self.model_cls = model_cls
        self.session = session

    async def get_item(self, item_id: int | str) -> ORM_MODEL:
        item = await self.session.get(self.model_cls, item_id)
        if item is None:
            raise raise_http_error(HTTPNotFound, f'{self.model_cls.__name__.lower()} not found')
        return item

    async def create_item(self, item: ORM_MODEL_CLS):
        self.session.add(item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(HTTPForbidden, f'such {self.model_cls.__name__.lower()} already exists')

    async def patch_item(self, params_json, item_id: int | str):
        item = await self.get(item_id)
        for field, value in params_json.items():
            setattr(item, field, value)
        self.session.add(item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(HTTPForbidden, f'attr already exists')

    async def delete_item(self, item_id):
        item = await self.get(item_id)
        await self.session.delete(item)
        await self.session.commit()
