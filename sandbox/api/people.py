from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_rel, filter_target_user
from .tools import check_profile_permissions


class Profile(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token')),
               'user': None}
        username = request.query_params.get('username')
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if cu and username:
            conn = await get_conn(request.app.config)
            target = await filter_target_user(request, conn, username)
            if target is None:
                res['message'] = f'{username}? Такого пользователя у нас нет.'
                await conn.close()
                return JSONResponse(res)
            if target and target['uid'] != cu.get('id') and \
                    permissions.FOLLOW not in cu['permissions']:
                res['message'] = 'Для вас доступ закрыт, увы.'
                await conn.close()
                return JSONResponse(res)
            res['user'] = target
            rel = await check_rel(conn, cu.get('id'), target.get('uid'))
            await check_profile_permissions(request, cu, target, rel, res)
            if res['address']:
                res['user']['address'] = await conn.fetchval(
                    'SELECT address FROM accounts WHERE user_id = $1',
                    res['user'].get('uid'))
            if res['ch-perms']:
                res['perms'] = [name.lower() for name in permissions._fields]
            await conn.close()
            return JSONResponse(res)
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
        text = d.get('text')
        if text:
            conn = await get_conn(request.app.config)
            await conn.execute(
                'UPDATE users SET description = $1 WHERE id = $2',
                text.strip()[:500], cu.get('id'))
            await conn.close()
            res['done'] = True
            await set_flashed(request, 'Описание блога обновлено.')
        return JSONResponse(res)
