import redis.asyncio as redis


async def get_rc(config):
    return redis.from_url(config.get('REDI'), decode_responses=True)
