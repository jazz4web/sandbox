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

from .admin.views import show_log, show_tools
from .announces.views import show_announce, show_announces
from .aliases.views import show_aliases
from .api.admin import Admin, Counter, DUPerms, IndexPage, Robots
from .api.aliases import Aliases
from .api.announces import Announce, Announces, Broadcast
from .api.arts import (
    Alabels, Art, Arts, CArt, Dislike, CArts, LCArts, Lenta, Like, LLenta)
from .api.auth import (
    ChangeAva, ChangeEmail, ChangePasswd, GetPasswd,
    Login, Logout, LogoutAll, RequestEm,
    RequestPasswd, ResetPasswd)
from .api.blogs import Authors, Blog, LBlog
from .api.comments import Answer, Comment
from .api.drafts import Draft, Drafts, Labels, Paragraph
from .api.main import Captcha, Index
from .api.people import People, Profile, Relation
from .api.pictures import Album, Albums, Albumstat, Picstat, Search, Ustat
from .api.pm import Conversation, Conversations
from .api.tasks import check_swapped
from .arts.views import (
    show_art, show_arts, show_author, show_cart, show_carts, show_followed,
    show_labeled_arts, show_labeled_author, show_labeled_c, show_labeled_f)
from .auth.attri import groups, permissions
from .blogs.views import show_blog, show_blogs, show_blog_l
from .captcha.views import show_captcha
from .dirs import base, static, templates, settings
from .drafts.views import show_draft, show_drafts, show_labeled
from .errors import show_error
from .main.views import (
    jump, show_avatar, show_favicon, show_index,
    show_picture, show_public, show_robots, show_sitemap)
from .people.views import show_people, show_profile
from .pictures.views import show_album, show_albums
from .pm.views import show_conversation, show_conversations

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
        Route('/robots.txt', show_robots, name='robots.txt'),
        Route('/sitemap.xml', show_sitemap, name='sitemap'),
        Route('/{suffix}', jump, name='jump'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Route('/captcha/{suffix}', show_captcha, name='captcha'),
        Route('/picture/{suffix}', show_picture, name='picture'),
        Route('/public/{slug}', show_public, name='public'),
        Mount('/admin', name='admin', routes=[
            Route('/', show_tools, name='tools'),
            Route('/logs/{log}', show_log, name='logs')]),
        Mount('/announces', name='announces', routes=[
            Route('/', show_announces, name='announces'),
            Route('/{suffix}', show_announce, name='announce')
            ]),
        Mount('/aliases', name='aliases', routes=[
            Route('/', show_aliases, name='aliases')]),
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
            Route('/pictures', Albums, name='aalbums'),
            Route('/pictures/{suffix}', Album, name='aalbum'),
            Route('/ustat', Ustat, name='austat'),
            Route('/albumstat', Albumstat, name='albumstat'),
            Route('/picstat', Picstat, name='apicstat'),
            Route('/search', Search, name='asearch'),
            Route('/drafts', Drafts, name='adrafts'),
            Route('/draft', Draft, name='adraft'),
            Route('/labels', Labels, name='alabel'),
            Route('/send-par', Paragraph, name='aparagraph'),
            Route('/blogs', Authors, name='ablogs'),
            Route('/blog', Blog, name='ablog'),
            Route('/arts', Arts, name='aarts'),
            Route('/alabels', Alabels, name='alabels'),
            Route('/lblog', LBlog, name='alblog'),
            Route('/lenta', Lenta, name='alenta'),
            Route('/llenta', LLenta, name='allenta'),
            Route('/people', People, name='apeople'),
            Route('/carts', CArts, name='acarts'),
            Route('/lcarts', LCArts, name='alcarts'),
            Route('/art', Art, name='aart'),
            Route('/follow', Lenta, name='afollow'),
            Route('/like', Like, name='alike'),
            Route('/dislike', Dislike, name='adislike'),
            Route('/cart', CArt, name='acart'),
            Route('/aliases', Aliases, name='aaliases'),
            Route('/announces', Announces, name='aannounces'),
            Route('/announce', Announce, name='aannounce'),
            Route('/broadcast', Broadcast, name='abroadcast'),
            Route('/admin-tools', Admin, name='aadmin'),
            Route('/chperms', DUPerms, name='adperms'),
            Route('/chrobots', Robots, name='arobots'),
            Route('/chindex', IndexPage, name='aindex'),
            Route('/setcounter', Counter, name='alic'),
            Route('/conv', Conversation, name='aconv'),
            Route('/convs', Conversations, name='aconvs'),
            Route('/comment', Comment, name='acomment'),
            Route('/answer', Answer, name='aanswer'),
            ]),
        Mount('/arts', name='arts', routes=[
            Route('/', show_arts, name='arts'),
            Route('/{slug}', show_art, name='art'),
            Route('/a/{username}', show_author, name='show-auth'),
            Route(
                '/a/{username}/t/{label}', show_labeled_author, name='lauth'),
            Route('/c/', show_carts, name='carts'),
            Route('/c/{slug}', show_cart, name='cart'),
            Route('/c/t/{label}', show_labeled_c, name='lcarts'),
            Route('/l/', show_followed, name='lenta'),
            Route('/l/t/{label}', show_labeled_f, name='llenta'),
            Route('/t/{label}', show_labeled_arts, name='labeled-arts'),
            ]),
        Mount('/blogs', name='blogs', routes=[
            Route('/', show_blogs, name='blogs'),
            Route('/{username}', show_blog, name='blog'),
            Route('/{username}/t/{label}', show_blog_l, name='blog-l')
            ]),
        Mount('/drafts', name='drafts', routes=[
            Route('/', show_drafts, name='drafts'),
            Route('/{slug}', show_draft, name='draft'),
            Route('/t/{label}', show_labeled, name='show-labeled')]),
        Mount('/people', name='people', routes=[
            Route('/', show_people, name='people'),
            Route('/{username}', show_profile, name='profile')
            ]),
        Mount('/pictures', name='pictures', routes=[
            Route('/', show_albums, name='albums'),
            Route('/{suffix}', show_album, name='album')]),
        Mount('/pm', name='pm', routes=[
            Route('/', show_conversations, name='conversations'),
            Route('/{username}', show_conversation, name='conversation')]),
        Mount('/static', app=StaticFiles(directory=static), name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
