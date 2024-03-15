from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_last, select_arts, select_labeled_arts


class Alabels(HTTPEndpoint):
    async def get(self, request):
        label = request.query_params.get('label')
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token')),
               'label': label}
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND articles.state IN ($2, $3)''',
            label, status.pub, status.priv)
        if page > last:
            res['message'] = f'Всего страниц: { last }.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_labeled_arts(
            request, conn, label, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        await conn.close()
        return JSONResponse(res)


class Arts(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last = await check_last(
            conn,
            page, request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM articles WHERE state IN ($1, $2)',
            status.pub, status.priv)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_arts(
            request, conn, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        await conn.close()
        return JSONResponse(res)
