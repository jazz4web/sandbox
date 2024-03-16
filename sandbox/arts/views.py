from starlette.responses import HTMLResponse, RedirectResponse

from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_labeled_author(request):
    username = request.path_params.get('username')
    label = request.path_params.get('label')
    url = request.url_for('blogs:blog-l', username=username, label=label)
    return RedirectResponse(url, 301)


async def show_author(request):
    username = request.path_params.get('username')
    url = request.url_for('blogs:blog', username=username)
    return RedirectResponse(url, 301)


async def show_labeled_arts(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/labeled-arts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'flashed': await get_flashed(request)})


async def show_arts(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/arts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_art(request):
    return HTMLResponse('<div>Not implemented yet.</div>')
