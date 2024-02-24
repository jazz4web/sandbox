import os

from starlette.responses import FileResponse, RedirectResponse

from ..common.flashed import get_flashed, set_flashed
from ..dirs import static


async def show_index(request):
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request)})

async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
