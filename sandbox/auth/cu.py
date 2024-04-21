import asyncio

import redis.asyncio as redis

from ..api.tasks import ping_user
from ..api.tokens import check_token
from ..auth.attri import get_group, permissions
from ..common.flashed import set_flashed
from ..common.redi import get_rc


async def checkcu(request, token):
    cache = await check_token(request.app.config, token)
    rc = await get_rc(request)
    if cache:
        data = await rc.hgetall(cache.get('cache'))
        if data:
            query = await rc.hgetall(f'data:{data["id"]}')
            uid = int(query.get('id'))
            if query and permissions.NOLOGIN in query.get('permissions'):
                await rc.delete(cache.get('cache'))
                await rc.delete(f'data:{uid}')
                await rc.close()
                return None
            if query:
                asyncio.ensure_future(
                    ping_user(request.app.config, uid))
                await rc.close()
                return {'id': uid,
                        'username': query.get('username'),
                        'group': await get_group(query.get('permissions')),
                        'registered': query.get('registered'),
                        'last_published': query.get('last_published'),
                        'permissions': query.get('permissions').split(','),
                        'ava': request.url_for(
                            'ava', username=query.get('username'),
                            size=22)._url,
                        'brkey': data.get('brkey')}
    else:
        if d := request.session.get('_uid'):
            await rc.delete(d)
            request.session.pop('_uid')
    await rc.close()
    return None


async def getcu(request):
    cache = request.session.get('_uid')
    if cache:
        rc = await get_rc(request)
        data = await rc.hgetall(cache)
        if data:
            query = await rc.hgetall(f'data:{data["id"]}')
            uid = int(query.get('id'))
            if query and permissions.NOLOGIN in query.get('permissions'):
                request.session.pop('_uid')
                await rc.delete(cache)
                await rc.delete(f'data:{uid}')
                await rc.close()
                await set_flashed(
                    request, 'Ваше присутствие в сервисе нежелательно.')
                return None
            if query:
                asyncio.ensure_future(
                    ping_user(request.app.config, uid))
                await rc.close()
                return {'id': uid,
                        'username': query.get('username'),
                        'group': await get_group(query.get('permissions')),
                        'registered': query.get('registered'),
                        'last_published': query.get('last_published'),
                        'permissions': query.get('permissions').split(','),
                        'ava': request.url_for(
                            'ava', username=query.get('username'),
                            size=22)._url,
                        'brkey': data.get('brkey')}
        else:
            request.session.pop('_uid')
        await rc.close()
    return None
