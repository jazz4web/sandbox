from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.aparsers import parse_page
from .attri import status


async def show_album(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'pictures/album.html',
        {'request': request,
         'suffix': request.path_params.get('suffix'),
         'page': await parse_page(request),
         'status': status,
         'flashed': await get_flashed(request)})


async def show_albums(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'pictures/albums.html',
        {'request': request,
         'cu': cu,
         'status': status,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
