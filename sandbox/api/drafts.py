import re

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import groups, permissions
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import (
    change_draft, check_draft, check_last, create_d,
    save_par, select_labeled_drafts, select_drafts, undress_art_links)


class Paragraph(HTTPEndpoint):
    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ART not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        slug, text, code = (
            d.get('slug', ''), d.get('text', ''), int(d.get('code', '0')))
        if not slug or not text:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        draft = await conn.fetchval(
            'SELECT id FROM articles WHERE slug = $1 AND author_id = $2',
            slug, cu.get('id'))
        if draft is None:
            res['message'] = 'Черновик не обнаружен.'
            await conn.close()
            return JSONResponse(res)
        res['html'] = await save_par(conn, draft, text, code)
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            draft)
        res['done'] = True
        await conn.close()
        return JSONResponse(res)


class Labels(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last =  await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = $1
                   AND articles.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND articles.state IN($3, $4)''',
            cu.get('id'), request.query_params.get('label'),
            status.draft, status.cens)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_labeled_drafts(
            request, conn, cu.get('id'), request.query_params.get('label'),
            res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'labels': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ART not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        slug, labels = d.get('slug', ''), d.get('labels', '')
        if not slug:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        draft = await conn.fetchval(
            'SELECT id FROM articles WHERE slug = $1 AND author_id = $2',
            slug, cu.get('id'))
        if draft is None:
            res['message'] = 'Черновик не обнаружен.'
            await conn.close()
            return JSONResponse(res)
        cur = [label.get('label') for label in await conn.fetch(
               '''SELECT labels.label FROM articles, labels, als
                    WHERE articles.id = als.article_id
                      AND labels.id = als.label_id
                      AND articles.id = $1''', draft)]
        new = [l.strip().lower() for l in labels.split(',') if l]
        for each in new:
            if not re.match(r'^[a-zа-яё\d\-]{1,32}$', each):
                res['message'] = 'Запрос содержит неверные параметры.'
                await conn.close()
                return JSONResponse(res)
        lq = 'SELECT id FROM labels WHERE label = $1'
        for each in cur:
            if each not in new:
                lid = await conn.fetchval(lq, each)
                await conn.execute(
                    '''DELETE FROM als WHERE article_id = $1
                         AND label_id = $2''', draft, lid)
        for each in new:
            if each not in cur:
                lid = await conn.fetchval(lq, each)
                if lid is None:
                    await conn.execute(
                        'INSERT INTO labels (label) VALUES ($1)', each)
                    lid = await conn.fetchval(lq, each)
                await conn.execute(
                    '''INSERT INTO als (article_id, label_id)
                         VALUES ($1, $2)''', draft, lid)
        res['labels'] = True
        await conn.close()
        await set_flashed(request, 'Метки установлены.')
        return JSONResponse(res)


class Draft(HTTPEndpoint):
    async def get(self, request):
        res = {'draft': None,
               'cu': await checkcu(
                   request, request.headers.get('x-auth-token'))}
        slug, cu = request.query_params.get('slug', ''), res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = dict()
        await check_draft(request, conn, slug, cu.get('id'), target)
        if not target:
            res['message'] = 'Ничего не нашлось по запросу.'
            await conn.close()
            return JSONResponse(res)
        res['length'] = await conn.fetchval(
            'SELECT count(*) FROM paragraphs WHERE article_id = $1',
            target.get('id'))
        res['chstate'] = True if target['meta'] and target['summary'] and \
                target['html'] and target['state'] != status.cens else False
        res['cens'] = target['state'] == status.cens
        res['keeper'] = cu.get('group') in (groups.keeper, groups.root)
        res['draft'] = target
        await conn.close()
        return JSONResponse(res)

    async def patch(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        draft = await conn.fetchrow(
            'SELECT id, author_id FROM articles WHERE slug = $1',
            d.get('slug', ''))
        if draft is None:
            res['message'] = 'Ничего не нашлось по запросу.'
            await conn.close()
            return JSONResponse(res)
        if (cu.get('id') == draft.get('author_id') and
            cu.get('group') not in (groups.keeper, groups.root)) or \
                    (cu.get('id') != draft.get('author_id') and
                     cu.get('group') != groups.root):
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        res['done'] = True
        await undress_art_links(conn, draft.get('id'))
        await set_flashed(request, 'Атрибут у ссылок удалён.')
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ART not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        field, value, slug = (
            d.get('field', ''), d.get('value', ''), d.get('slug', ''))
        if not all((field, value, slug)):
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        draft = await conn.fetchval(
            'SELECT id FROM articles WHERE slug = $1 AND author_id = $2',
            d.get('slug', ''), cu.get('id'))
        s = await change_draft(request, conn, draft, field, value)
        res['done'] = True
        if s:
            res['slug'] = s
        await set_flashed(request, 'Изменено успешно.')
        await conn.close()
        return JSONResponse(res)


class Drafts(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last = await check_last(
            conn,
            page, request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3)''',
            cu.get('id'), status.draft, status.cens)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_drafts(
            request, conn, cu.get('id'), res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        res['extra'] = not res['pagination'] or \
                (res['pagination'] and res['pagination']['page'] == 1)
        res['canwrite'] = permissions.ART in cu['permissions']
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'draft': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ART not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        title = d.get('title', '')
        if not title or len(title.strip()) > 100:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        slug = await create_d(conn, title.strip(), cu.get('id'))
        await conn.close()
        res['draft'] = request.url_for('drafts:draft', slug=slug)._url
        return JSONResponse(res)

