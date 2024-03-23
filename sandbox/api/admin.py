from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import initials, permissions
from ..auth.cu import checkcu
from ..common.pg import get_conn


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
        res['robots'] = await request.app.rc.get('robots:page') or \
                request.app.jinja.get_template(
                'main/robots.txt').render(request=request)
        res['index'] = await request.app.rc.get('index:page')
        res['li_counter'] = await request.app.rc.get('li:counter')
        await conn.close()
        return JSONResponse(res)
