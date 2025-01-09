from fastapi import APIRouter, Request, Response,Query
from imageservice.utils import Metadata, ResponseModel
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/list",response_model=ResponseModel)
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
        if images:
            if len(images.get("thumbnails")) > 0:
                return JSONResponse(
                    content=images,
                    status_code=200
                )
            else:
                return JSONResponse(
                    content={"Error": "User not found"},
                    status_code=404
                ) 
        else:
            return JSONResponse(
                content=None,
                status_code=500
            )             
    
    except Exception as e:
        return JSONResponse(
            content=f"Failed to fetch: {e}",
            status_code=500
        )