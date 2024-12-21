import base64
import io,os
import uuid
from fastapi import APIRouter,Request, Response
from PIL import Image
from utils import Metadata

router = APIRouter()

@router.post("/upload")
async def upload_image(request:Request):
    body = request.body()
    userId = request.query_params.get("userId")
    try:
        image_bytes = base64.b64decode(body)
        image = Image.open(io.BytesIO(image_bytes))
        md = Metadata(userId=userId)
        md.write_image(image)

        return Response(
            content="Successfully uploaded",
            status_code=200
        )
        
    except Exception as e:
        return Response(
            content=f"Failed to upload: {e}",
            status_code=500
        )