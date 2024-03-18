from starlette.responses import HTMLResponse, RedirectResponse

from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_cart(request):
    return HTMLResponse('<div>Not implemented yet.</div>')


async def show_art(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/art.html',
        {'request': request,
         'cu': cu,
         'slug': request.path_params.get('slug'),
         'flashed': await get_flashed(request)})


async def show_labeled_c(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/lcarts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'flashed': await get_flashed(request)})


async def show_carts(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/carts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_labeled_f(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/llenta.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'flashed': await get_flashed(request)})


async def show_followed(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/lenta.html',
        {'request': request,
         'page': await parse_page(request),
         'cu': cu,
         'flashed': await get_flashed(request)})


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
