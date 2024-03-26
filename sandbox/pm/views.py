from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed


async def show_conversations(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'pm/conversations.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})


async def show_conversation(request):
    cu = await getcu(request)
    return request.app.jinja.TemplateResponse(
        'pm/conversation.html',
        {'request': request,
         'cu': cu,
         'username': request.path_params.get('username'),
         'page': await parse_page(request),
         'nopage': request.query_params.get('page', '0'),
         'flashed': await get_flashed(request)})
