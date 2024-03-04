async def parse_page(request):
    page=request.query_params.get('page', None)
    try:
        page = int(page)
    except (ValueError, TypeError):
        return 1
    return page or 1
