
from fastapi import APIRouter, Request,Response
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/")
async def homepage(request: Request):
    return JSONResponse({"message": 'Hello from Image service API'})