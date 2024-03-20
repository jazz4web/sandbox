from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_announce(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'announces/announce.html',
        {'request': request,
         'cu': cu,
         'suffix': request.path_params.get('suffix'),
         'flashed': await get_flashed(request)})


async def show_announces(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'announces/announces.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
