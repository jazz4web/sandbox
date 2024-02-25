from ..common.pg import get_conn


async def ping_user(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'UPDATE users SET last_visit = $1 WHERE id = $2',
        datetime.utcnow(), uid)
    await conn.close()
