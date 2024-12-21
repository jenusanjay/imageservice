from fastapi import APIRouter,Request,Response
from utils import Metadata,MetadataInputModel


router = APIRouter()

@router.get("/view")
def view_image(request:Request):
    """
    API used to view image
    - **userId**: The userID of the item to view in query parameters
    - **timestamp**: The timestamp of the image creation in the App
    """
    userId = request.query_params.get("userId")
    timestamp = request.query_params.get("timestamp")
    try:
        md = Metadata(userId=userId)
        image = md.get_item(itemInfo=MetadataInputModel(
            userId=userId,
            timestamp=timestamp
        ))
        
        return Response(
            content=image,
            status_code=200
        )
        
    except Exception as e:
        return Response(
            content=f"Failed to fetch: {e}",
            status_code=500
        )