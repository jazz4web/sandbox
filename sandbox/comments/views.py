from ..auth.cu import getcu
from ..common.aparsers  import parse_page
from ..common.flashed import get_flashed


async def show_comments(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'comments/comments.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
