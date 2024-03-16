from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_people(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'people/people.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


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
