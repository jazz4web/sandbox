from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.redi import get_rc


async def show_blog_l(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counters')
    await rc.close()
    return request.app.jinja.TemplateResponse(
        'blogs/labeled.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'counters': counters,
         'label': request.path_params.get('label'),
         'username': request.path_params.get('username'),
         'flashed': await get_flashed(request)})


async def show_blog(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counters')
    await rc.close()
    return request.app.jinja.TemplateResponse(
        'blogs/blog.html',
        {'request': request,
         'cu': cu,
         'counters': counters,
         'page': await parse_page(request),
         'username': request.path_params.get('username'),
         'flashed': await get_flashed(request)})


async def show_blogs(request):
    cu = await getcu(request)
    rc = await get_rc(request)
    counters = await rc.get('li:counters')
    await rc.close()
    return request.app.jinja.TemplateResponse(
        'blogs/authors.html',
        {'request': request,
         'cu': cu,
         'counters': counters,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
