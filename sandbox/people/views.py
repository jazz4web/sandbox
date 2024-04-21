from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.redi import get_rc


async def show_people(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counter')
    await rc.close()
    return request.app.jinja.TemplateResponse(
        'people/people.html',
        {'request': request,
         'cu': cu,
         'counters': counters,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_profile(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counter')
    await rc.close()
    interval = request.app.config.get('REQUEST_INTERVAL', cast=float)
    return request.app.jinja.TemplateResponse(
        'people/profile.html',
        {'request': request,
         'cu': cu,
         'counters': counters,
         'username': request.path_params.get('username'),
         'interval': interval,
         'flashed': await get_flashed(request)})
