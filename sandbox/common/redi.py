import redis.asyncio as redis


async def get_rc(request):
    return redis.Redis.from_pool(request.app.rp)
#   return redis.from_url(config.get('REDI'), decode_responses=True)
