import asyncio
import functools
import os

from starlette.exceptions import HTTPException
from starlette.responses import (
    HTMLResponse, FileResponse, PlainTextResponse, RedirectResponse, Response)

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..dirs import static
from ..errors import E404
from ..pictures.attri import status
from .pg import check_state, check_topic
from .tools import resize


async def show_robots(request):
    text = await request.app.rc.get('robots:page') or \
            request.app.jinja.get_template(
                    'main/robots.txt').render(request=request)
    return PlainTextResponse(text)


async def show_public(request):
    slug = request.path_params.get('slug')
    cu = await getcu(request)
    if cu:
        return RedirectResponse(request.url_for('arts:art', slug=slug), 301)
    topic = dict()
    conn = await get_conn(request.app.config)
    await check_topic(request, conn, slug, topic)
    if not topic:
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    return request.app.jinja.TemplateResponse(
        'main/show-public.html',
        {'request': request,
         'topic': topic})


async def show_sitemap(request):
    conn = await get_conn(request.app.config)
    arts = await conn.fetch(
        '''SELECT slug, published, edited FROM articles
             WHERE state = $1 ORDER BY published DESC LIMIT 250''',
        status.pub)
    await conn.close()
    response = request.app.jinja.TemplateResponse(
        'main/sitemap.xml',
        {'request': request,
         'arts': arts})
    response.media_type = 'application/xml'
    response.headers['content-type'] = 'application/xml'
    return response


async def jump(request):
    suffix = request.path_params.get('suffix')
    return HTMLResponse('<div>Not implemented yet.</div>')


async def show_picture(request):
    cu = await getcu(request)
    conn = await get_conn(request.app.config)
    target = await conn.fetchrow(
        '''SELECT albums.state, albums.author_id, pictures.suffix,
                  pictures.picture, pictures.format FROM albums, pictures
             WHERE pictures.suffix = $1
             AND albums.id = pictures.album_id''',
            request.path_params.get('suffix'))
    if target is None:
        response = FileResponse(
            os.path.join(static, 'images', '404.png'))
        response.headers.append(
            'cache-control',
            'max-age=0, no-store, no-cache, must-revalidate')
    else:
        if await check_state(conn, target, cu):
            response = Response(
                target.get('picture'),
                media_type=f'image/{target.get("format").lower()}')
            response.headers.append(
                'cache-control',
                'public, max-age={0}'.format(
                    request.app.config.get(
                        'SEND_FILE_MAX_AGE', cast=int, default=0)))
        else:
            if target['state'] == status.ffo:
                picname = '403a.png'
            else:
                picname = '403.png'
            response = FileResponse(
                os.path.join(static, 'images', picname))
            response.headers.append(
                'cache-control',
                'max-age=0, no-store, no-cache, must-revalidate')
    await conn.close()
    return response


async def show_avatar(request):
    size = request.path_params['size']
    if size < 22 or size > 160:
        raise HTTPException(status_code=404, detail=E404)
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT id, username FROM users WHERE username = $1',
        request.path_params['username'])
    if res is None:
        raise HTTPException(status_code=404, detail=E404)
    ava = await conn.fetchval(
        'SELECT picture FROM avatars WHERE user_id = $1', res.get('id'))
    await conn.close()
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(
        None, functools.partial(resize, size, ava))
    response = Response(image, media_type='image/png')
    if ava is None:
        response.headers.append('cache-control', 'public, max-age=0')
    else:
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'SEND_FILE_MAX_AGE', cast=int, default=0)))
    return response


async def show_index(request):
    cu = await getcu(request)
    interval = request.app.config.get('REQUEST_INTERVAL', cast=float)
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'cu': cu,
         'interval': interval,
         'flashed': await get_flashed(request)})


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
