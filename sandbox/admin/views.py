import os

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, PlainTextResponse

from ..auth.attri import get_group, groups
from ..common.pg import get_conn


async def show_log(request):
    l = request.path_params.get('log')
    if l not in ('access.log', 'previous.log'):
        raise HTTPException(404, detail='Такой страницы у нас нет.')
    cu = int((await request.app.rc.hgetall(
        request.session.get('_uid', 'empty'))).get('id', '0'))
    if cu:
        conn = await get_conn(request.app.config)
        cu = await conn.fetchrow(
            'SELECT id, permissions FROM users WHERE id = $1', cu)
        if cu:
            group = await get_group(cu.get('permissions'))
            if group in (groups.keeper, groups.root):
                if l == 'access.log':
                    l = f'/var/log/nginx/{l}'
                else:
                    l = '/var/log/nginx/access.log.1'
                if os.path.exists(l):
                    response = FileResponse(l)
                else:
                    a = 'Файл не существует.\n'
                    m = 'Убедитесь, что вы используете Nginx.'
                    response = PlainTextResponse(a + m)
                return response
    raise HTTPException(404, detail='Такой страницы у нас нет.')
