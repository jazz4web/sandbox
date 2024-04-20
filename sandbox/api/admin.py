import re

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.attri import initials, permissions, USER_PATTERN
from ..auth.cu import checkcu
from ..auth.pg import check_username, create_user
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..common.redi import get_rc
from ..drafts.attri import status


class Counter(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        val = d.get('value', '')
        rc = await get_rc(request.app.config)
        if val:
            await rc.set('li:counter', val)
            await set_flashed(request, 'Счётчики установлены.')
        else:
            await rc.delete('li:counter')
            await set_flashed(request, 'Счётчики удалёны.')
        await rc.aclose()
        res['done'] = True
        return JSONResponse(res)


class IndexPage(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        val = d.get('value', '')
        rc = await get_rc(request.app.config)
        if val:
            conn = await get_conn(request.app.config)
            d = await conn.fetchval(
                '''SELECT suffix FROM articles
                     WHERE suffix = $1 AND author_id = $2 AND state = $3''',
                val, cu.get('id'), status.draft)
            if d:
                await rc.set('index:page', d)
            else:
                res['message'] = 'Ничего не найдено по суффиксу.'
                return JSONResponse(res)
        else:
            await rc.delete('index:page')
        await rc.aclose()
        res['done'] = True
        return JSONResponse(res)


class Robots(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        val = d.get('value', '')
        rc = await get_rc(request.app.config)
        if val:
            await rc.set('robots:page', val)
        else:
            await rc.delete('robots:page')
        await rc.aclose()
        res['done'] = True
        return JSONResponse(res)


class DUPerms(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        names = {each: bool(int(d.get(each))) for each in d if each != 'auth'}
        conn = await get_conn(request.app.config)
        cur = [r.get('name') for r in await conn.fetch(
            '''SELECT name, init FROM permissions
                 WHERE name = any($1::varchar[])''', [name for name in names])
            if names.get(r.get('name')) != r.get('init')]
        for each in cur:
            await conn.execute(
                'UPDATE permissions SET init = $1 WHERE name = $2',
                names[each], each)
        res['done'] = True
        await conn.close()
        await set_flashed(request, 'Разрешения по-умолчанию изменены.')
        return JSONResponse(res)


class Admin(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        perms = await conn.fetch(
            'SELECT * FROM permissions WHERE permission = any($1::varchar[])',
            [key for key in initials])
        res['perms'] = request.app.jinja.get_template(
            'admin/perms.html').render(request=request, permissions=perms)
        rc = await get_rc(request.app.config)
        res['robots'] = await rc.get('robots:page') or \
                request.app.jinja.get_template(
                'main/robots.txt').render(request=request)
        res['index'] = await rc.get('index:page')
        res['li_counter'] = await rc.get('li:counter')
        await rc.aclose()
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        username, address, password, confirma = (
            d.get('username'), d.get('address'),
            d.get('password'), d.get('confirma'))
        if not all((username, address, password, confirma)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        if password != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.ADMINISTER not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        p = re.compile(USER_PATTERN)
        if not p.match(username):
            res['message'] = 'Псевдоним не удовлетворяет требованиям сервиса.'
            return JSONResponse(res)
        if await check_username(request.app.config, username):
            res['message'] = f'Псеводним {username} уже зарегистрирован.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchval(
            'SELECT user_id FROM accounts WHERE address = $1', address)
        swapped = await conn.fetchval(
            'SELECT swap FROM accounts WHERE swap = $1', address)
        if acc or swapped:
            res['message'] = f'Адрес {address} уже используется.'
            await conn.close()
            return JSONResponse(res)
        perms = [each.get('permission') for each in await conn.fetch(
            'SELECT permission FROM permissions WHERE init = true')]
        await conn.close()
        await create_user(
            request.app.config, username, address, password, perms)
        res['redirect'] = request.url_for(
            'people:profile', username=username)._url
        res['done'] = True
        await set_flashed(request, f'Аккаунт {username} успешно создан.')
        return JSONResponse(res)
