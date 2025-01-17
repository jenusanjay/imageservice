import base64
import io,os
import uuid
from fastapi import APIRouter, Query,Request, Body
from PIL import Image
from imageservice.utils import Metadata, ResponseModel
from starlette.responses import JSONResponse

router = APIRouter()

@router.post("/upload",response_model=ResponseModel)
async def upload_image(request:Request,
                        userId: str = Query(default=None, description="Id of the User to Upload images"),
                        image: str = Body(default=None, description="Id of the User to Upload images")):
    """
    API used to upload images
    - **userId**: The userID of the item to upload in query parameters
    - **body**: Image bytes to be sent in request body
    """

    body = await request.body()
    userId = request.query_params.get("userId")
    try:
        image_bytes = base64.b64decode(body)
        image = Image.open(io.BytesIO(image_bytes))
        md = Metadata(userId=userId)
        md.write_image(image,image_bytes)

        return JSONResponse(
            content="Successfully uploaded",
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content=f"Failed to upload: {e}",
            status_code=500
        )