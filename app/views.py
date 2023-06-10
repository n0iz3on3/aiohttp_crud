from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp.web import View, Request, Response, json_response, HTTPUnauthorized

from crud import SQLAlchemyCRUD
from errors import raise_http_error
from models import User, Ads, Token
from auth import hash_password, check_password, check_owner
from schema import Register, Login, PatchUser, CreateAds, PatchAds, validate


class UserLogin(View):
    @validate(Login)
    async def post(self) -> Response:
        login_data = await self.request.json()
        query = select(User).where(User.email == login_data['email'])
        result = await self.request['session'].execute(query)
        user = result.scalar()

        if user is None or not await check_password(user.password, login_data['password']):
            raise raise_http_error(HTTPUnauthorized, {'error': 'user or password is incorrect'})

        token = Token(user=user)
        self.request['session'].add(token)
        await self.request['session'].commit()
        return json_response({'token': f'{token.id}'})


class UserView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.crud = SQLAlchemyCRUD(self.session, User)

    @property
    def session(self) -> AsyncSession:
        return self.request['session']

    @property
    def user_id(self) -> int:
        return int(self.request.match_info['user_id'])

    async def get(self) -> Response:
        user = await self.crud.get_item(self.user_id)
        return json_response(
            {
                'id': user.id,
                'email': user.email,
                'creation_time': user.creation_time.isoformat(),
            }
        )

    @validate(Register)
    async def post(self) -> Response:
        register_data = await self.request.json()
        register_data['password'] = await hash_password(register_data['password'])
        user = User(**register_data)
        await self.crud.create_item(user)
        return json_response({'user': f'id - {user.id}'})

    @validate(PatchUser)
    async def patch(self) -> Response:
        await check_owner(self.request, self.user_id)
        user = await self.crud.get_item(self.user_id)
        user_data = await self.request.json()

        if 'password' in user_data:
            user_data['password'] = await hash_password(user_data['password'])

        await self.crud.patch_item(user_data, self.user_id)
        return json_response(
            {
                'id': user.id,
                'email': user.email,
                'creation_time': user.creation_time.isoformat(),
            }
        )

    async def delete(self) -> Response:
        await check_owner(self.request, self.user_id)
        await self.crud.delete_item(self.user_id)
        return json_response(
            {
                'status': 'deleted'
            }
        )


class AdsView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.crud = SQLAlchemyCRUD(self.session, Ads)

    @property
    def session(self) -> AsyncSession:
        return self.request['session']

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info['adv_id'])

    @property
    async def owner_id(self) -> int:
        advert = await self.crud.get_item(self.adv_id)
        return int(advert.owner_id)

    @property
    async def user_id(self) -> int:
        return self.request['token'].user.id

    async def get(self) -> Response:
        adv = await self.crud.get_item(self.adv_id)
        return json_response(
            {
                'id': adv.id,
                'title': adv.title,
                'description': adv.description,
                'owner_id': adv.owner_id,
                'creation_time': adv.creation_time.isoformat(),
            }
        )

    @validate(CreateAds)
    async def post(self) -> Response:
        adv_data = await self.request.json()
        adv_data['owner_id'] = await self.user_id
        adv = Ads(**adv_data)
        await self.crud.create_item(adv)
        return json_response(
            {
                'id': adv.id,
                'title': adv.title,
                'description': adv.description,
                'owner_id': adv.owner_id,
            }
        )

    @validate(PatchAds)
    async def patch(self) -> Response:
        await check_owner(self.request, await self.owner_id)
        adv = await self.crud.get_item(self.adv_id)
        adv_data = await self.request.json()
        await self.crud.patch_item(adv_data, self.adv_id)
        return json_response(
            {
                'id': adv.id,
                'title': adv.title,
                'description': adv.description,
                'owner_id': adv.owner_id,
                'creation_time': adv.creation_time.isoformat(),
            }
        )

    async def delete(self) -> Response:
        await check_owner(self.request, await self.owner_id)
        await self.crud.delete_item(self.adv_id)
        return json_response({'status': 'deleted'})
