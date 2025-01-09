
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from imageservice.utils import ResponseModel

router = APIRouter()
@router.get("/",response_model=ResponseModel)
async def homepage(request: Request):
    return JSONResponse({"message": 'Hello from Image service API'})