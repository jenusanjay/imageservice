import ast
from decimal import Decimal
import json
from fastapi import APIRouter, Query,Request,Response
from imageservice.utils import Metadata,MetadataInputModel, ResponseModel
from starlette.responses import JSONResponse


router = APIRouter()

@router.get("/view",response_model=ResponseModel)
def view_image(request:Request,
                userId: str = Query(default=None, description="Id of the User to view images"),
                 timestamp: Decimal = Query(default=None, description="Timestamp of the image creation")):
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
            timestamp=Decimal(timestamp)
        ))
        return JSONResponse(
            content=image,
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content=f"Failed to fetch: {e}",
            status_code=500
        )