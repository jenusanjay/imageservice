from fastapi import APIRouter, Request, Response
from utils import Metadata
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/list")
def delete_image(request:Request):
    """
    API used to list images
    - **userId**: The userID of the item to upload in query parameters
    """
    userId = request.query_params.get("userId")
    try:
        md = Metadata(userId=userId)
        images = md.get_items(
        )
        return JSONResponse(
            content=images,
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content=f"Failed to fetch: {e}",
            status_code=500
        )