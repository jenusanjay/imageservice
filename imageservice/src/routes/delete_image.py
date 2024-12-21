from fastapi import APIRouter, Query,Request,Response
from utils import Metadata, MetadataInputModel
from starlette.responses import JSONResponse

router = APIRouter()

@router.post("/delete")
def delete_image(request:Request,
                 userId: str = Query(default=None, description="Id of the User to delete images"),
                 timestamp: int = Query(default=None, description="Timestamp of the image creation")):
    """
    API used to delete image
    - **userId**: The userID of the item to view in query parameters
    - **timestamp**: The timestamp of the image creation in the App
    """
    userId = request.query_params.get("userId")
    timestamp = request.query_params.get("timestamp")
    try:
        md = Metadata(userId=userId)
        image = md.delete_item(itemInfo=MetadataInputModel(
            userId=userId,
            timestamp=timestamp
        ))
        return JSONResponse(
            content="Successfully delete image",
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=f"Failed to fetch: {e}",
            status_code=500
        )