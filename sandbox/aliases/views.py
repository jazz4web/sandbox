from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.redi import get_rc


async def show_aliases(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counter')
    await rc.close()
    return request.app.jinja.TemplateResponse(
        'aliases/aliases.html',
        {'request': request,
         'cu': cu,
         'counters': counters,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
