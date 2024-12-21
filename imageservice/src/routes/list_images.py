from fastapi import APIRouter, Request, Response
from utils import Metadata

router = APIRouter()

@router.post("/list")
def delete_image(request:Request):
    userId = request.query_params.get("userId")
    try:
        md = Metadata(userId=userId)
        images = md.get_items(
        )
        return Response(
            content=images,
            status_code=200
        )
        
    except Exception as e:
        return Response(
            content=f"Failed to fetch: {e}",
            status_code=500
        )