from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse


class Index(HTTPEndpoint):
    async def get(self, request):
        res = {'empty': True}
        return JSONResponse(res)
