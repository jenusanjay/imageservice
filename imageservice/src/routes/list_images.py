from fastapi import APIRouter, Request, Response,Query
from utils import Metadata
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/list")
def list_images(request:Request,
                userId: str = Query(default=None, description="Id of the User to get images")):
    
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