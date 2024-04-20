from ..common.random import randomize
from ..common.redi import get_rc


async def change_udata(config, data, permissions):
    rc = await get_rc(config)
    if await rc.exists(data):
        await rc.hset(data, key='permissions', value=','.join(permissions))
    await rc.aclose()


async def assign_uid(request, prefix, remember_me, user, brkey):
    if remember_me:
        expiration = request.app.config.get('SESSION_LIFETIME')
    else:
        expiration = 2 * 60 * 60
    rc = await get_rc(request.app.config)
    cache = await get_unique(rc, prefix, 9)
    await rc.hmset(cache, {'id': user.get('id'), 'brkey': brkey})
    await rc.expire(cache, expiration)
    data = f'data:{user.get("id")}'
    existed = await rc.exists(data)
    await rc.hmset(
        data, {'id': user.get('id'),
               'username': user.get('username'),
               'registered': f"{user.get('registered').isoformat()}Z",
               'last_published': f"{user.get('last_published').isoformat()}Z"
               if user.get('last_published') else 0,
               'permissions': ','.join(user.get('permissions')),
               'many': 0})
    if existed:
        await rc.hset(data, key='many', value=1)
        if remember_me:
            await rc.persist(data)
            await rc.expire(data, expiration)
        else:
            if await rc.ttl(data) < expiration:
                await rc.persist(data)
                await rc.expire(data, expiration)
    else:
        await rc.expire(data, expiration)
    await rc.aclose()
    return cache


async def extract_cache(config, cache):
    rc = await get_rc(config)
    suffix, val = await rc.hmget(cache, 'suffix', 'val')
    await rc.aclose()
    return suffix, val


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_cache(config, prefix, suffix, val, expiration):
    rc = await get_rc(config)
    cache = await get_unique(rc, prefix, 6)
    await rc.hmset(cache, {'suffix': suffix, 'val': val})
    await rc.expire(cache, expiration)
    await rc.aclose()
    return cache
