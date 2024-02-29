from ..auth.cu import getcu
from ..common.flashed import get_flashed


async def show_profile(request):
    cu = await getcu(request)
    interval = request.app.config.get('REQUEST_INTERVAL', cast=float)
    return request.app.jinja.TemplateResponse(
        'people/profile.html',
        {'request': request,
         'cu': cu,
         'username': request.path_params.get('username'),
         'interval': interval,
         'flashed': await get_flashed(request)})
