import os

from starlette.responses import FileResponse, RedirectResponse

from ..dirs import static

async def show_index(request):
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request})

async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
