from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_labeled(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'drafts/labeled.html',
        {'request': request,
         'cu': cu,
         'label': request.path_params.get('label'),
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_draft(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'drafts/draft.html',
        {'request': request,
         'cu': cu,
         'slug': request.path_params.get('slug'),
         'flashed': await get_flashed(request)})


async def show_drafts(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'drafts/drafts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
