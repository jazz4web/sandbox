from starlette.responses import HTMLResponse
from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed


async def show_announce(request):
    return HTMLResponse('<div>Not implemented yet.</div>')


async def show_announces(request):
    cu = await getcu(request)
    await set_flashed(request, 'Тест.')
    await set_flashed(request, 'Test2.')
    return request.app.jinja.TemplateResponse(
        'announces/announces.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
