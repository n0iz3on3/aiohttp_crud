from typing import AsyncGenerator
from aiohttp.web import Application, delete, get, post, patch, run_app

from models import Base, engine
from views import UserView, AdsView, UserLogin
from middlewares import check_auth_middleware, session_middleware


async def orm_context(app: Application) -> AsyncGenerator:
    print('start')
    async with engine.begin() as db_conn:
        await db_conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('shut down')


async def main() -> Application:
    app = Application()
    app.middlewares.append(session_middleware)
    # app.middlewares.append(check_auth_middleware)
    app_auth_users = Application(middlewares=[session_middleware, check_auth_middleware])
    app_auth_ads = Application(middlewares=[session_middleware, check_auth_middleware])
    app.cleanup_ctx.append(orm_context)

    app.add_routes(
        [
            get('/users/{user_id:\d+}', UserView),
            get('/ads/{adv_id:\d+}', AdsView),
            post('/login', UserLogin),
            post('/users', UserView)
        ]
    )

    app_auth_users.add_routes(
        [
            patch('/{user_id:\d+}', UserView),
            delete('/{user_id:\d+}', UserView)
        ]
    )

    app_auth_ads.add_routes(
        [
            post('', AdsView),
            patch('/{adv_id:\d+}', AdsView),
            delete('/{adv_id:\d+}', AdsView)
        ]
    )

    app.add_subapp(prefix='/users', subapp=app_auth_users)
    app.add_subapp(prefix='/ads', subapp=app_auth_ads)
    return app


run_app(main())
