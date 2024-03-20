import asyncio
import functools

from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..common.random import get_unique_s
from .md import html_ann
from .pg import check_last, select_announces


class Announces(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ANNOUNCE not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last = await check_last(
            conn, page,
            request.app.config.get('ANNS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM announces WHERE author_id = $1',
            cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_announces(
            conn, cu.get('id'), res['pagination'], page,
            request.app.config.get('ANNS_PER_PAGE', cast=int, default=3), last)
        res['extra'] = not res['pagination'] or \
                (res['pagination'] and res['pagination']['page'] == 1)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'announce': None}
        d = await request.form()
        title, text, heap = (
            d.get('title', ''), d.get('text', ''), int(d.get('heap', '0')))
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ANNOUNCE not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        if not all((title, text)) or len(title) > 50 or len(text) > 1024:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        loop = asyncio.get_running_loop()
        html = await loop.run_in_executor(
            None, functools.partial(html_ann, text))
        conn = await get_conn(request.app.config)
        suffix = await get_unique_s(conn, 'announces', 6)
        await conn.execute(
            '''INSERT INTO announces (headline, body, html, suffix, pub,
                                      adm, published, author_id)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)''',
            title, text, html, suffix, bool(heap),
            permissions.ADMINISTER in cu['permissions'],
            datetime.utcnow(), cu.get('id'))
        await conn.close()
        res['announce'] = request.url_for(
            'announces:announce', suffix=suffix)._url
        mes = 'Новое объявление создано.'
        if heap:
            mes = 'Новое объявление создано и опубликовано.'
        await set_flashed(request, mes)
        return JSONResponse(res)
