import asyncio

from ..api.tasks import ping_user
from ..auth.attri import get_group, permissions


async def getcu(request):
    cache = request.session.get('_uid')
    if cache:
        data = await request.app.rc.hgetall(cache)
        if data:
            query = await request.app.rc.hgetall(f'data:{data["id"]}')
            uid = int(query.get('id'))
            if query and permissions.NOLOGIN in query.get('permissions'):
                await request.app.rc.delete(cache)
                await request.app.rc.delete(f'data:{uid}')
                return None
            if query:
                asyncio.ensure_future(
                    ping_user(request.app.config, uid))
                return {'id': uid,
                        'username': query.get('username'),
                        'group': await get_group(query.get('permissions')),
                        'registered': query.get('registered'),
                        'last_published': query.get('last_pablished'),
                        'permissions': query.get('permissions').split(','),
                        'ava': request.url_for(
                            'ava', username=query.get('username'),
                            size=22)._url,
                        'brkey': data.get('brkey')}
        else:
            del request.session['_uid']
    return None
