from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_aliases(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'aliases/aliases.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
