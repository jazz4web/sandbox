import jinja2
import typing

from redis import asyncio as aioredis
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, Route
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .api.main import Captcha, Index
from .api.auth import (
    ChangeAva, ChangeEmail, ChangePasswd, GetPasswd,
    Login, Logout, LogoutAll, RequestEm,
    RequestPasswd, ResetPasswd)
from .api.people import Profile, Relation
from .api.tasks import check_swapped
from .auth.attri import groups, permissions
from .captcha.views import show_captcha
from .dirs import base, static, templates, settings
from .errors import show_error
from .main.views import show_avatar, show_index, show_favicon
from .people.views import show_profile

try:
    from .tuning import SITE_NAME, SITE_DESCRIPTION, SECRET_KEY, MAIL_PASSWORD
    if SITE_NAME:
        settings.file_values["SITE_NAME"] = SITE_NAME
    if SITE_DESCRIPTION:
        settings.file_values["SITE_DESCRIPTION"] = SITE_DESCRIPTION
    if SECRET_KEY:
        settings.file_values["SECRET_KEY"] = SECRET_KEY
    if MAIL_PASSWORD:
        settings.file_values["MAIL_PASSWORD"] = MAIL_PASSWORD
except ModuleNotFoundError:
    pass

DI = '''typing.Union[srt, os.PathLike[typing.AnyStr],
typing.Sequence[typing.Union[str,
os.PathLike[typing.AnyStr]]]]'''.replace('\n', ' ')


class J2Templates(Jinja2Templates):
    def _create_env(
            self,
            directory: DI, **env_options: typing.Any) -> "jinja2.Environment":
        loader = jinja2.FileSystemLoader(directory)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', bool)
        env_options.setdefault("loader", loader)
        env_options.setdefault("autoescape", True)
        env_options.setdefault("extensions", [assets])
        env = jinja2.Environment(**env_options)
        env.assets_environment = assets_env
        env.globals.setdefault("permissions", permissions)
        env.globals.setdefault("groups", groups)
        return env


class StApp(Starlette):
   async def __call__(
           self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        self.config = settings
        self.jinja = J2Templates(directory=templates)
        self.rc = aioredis.from_url(
            settings.get('REDI'), decode_responses=True)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)


async def run_before():
    await check_swapped(settings)


middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.get('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int))]

errs = {404: show_error}

app = StApp(
    debug=settings.get('DEBUG', cast=bool),
    routes=[
        Route('/', show_index, name='index'),
        Route('/favicon.ico', show_favicon, name='favicon'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Route('/captcha/{suffix}', show_captcha, name='captcha'),
        Mount('/api', name='api', routes=[
            Route('/index', Index, name='aindex'),
            Route('/captcha', Captcha, name='acaptcha'),
            Route('/login', Login, name='alogin'),
            Route('/logout', Logout, name='alogout'),
            Route('/logout-all', LogoutAll, name='alogoutall'),
            Route('/request-reg', GetPasswd, name='agetpasswd'),
            Route('/request-passwd', RequestPasswd, name='arequestpwd'),
            Route('/reset-passwd', ResetPasswd, name='aresetpwd'),
            Route('/profile', Profile, name='aprofile'),
            Route('/change-ava', ChangeAva, name='chava'),
            Route('/change-passwd', ChangePasswd, name='chpwd'),
            Route('/request-email-change', RequestEm, name='rem-change'),
            Route('/change-email', ChangeEmail, name='change-email'),
            Route('/rel', Relation, name='arel'),
            ]),
        Mount('/people', name='people', routes=[
            Route('/{username}', show_profile, name='profile')
            ]),
        Mount('/static', app=StaticFiles(directory=static), name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
