async def show_error(request, exc):
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'error': exc.status_code},
        status_code=exc.status_code)
