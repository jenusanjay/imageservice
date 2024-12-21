from fastapi import APIRouter,Request,Response
from assignment.imageservice.src.utils import Metadata, MetadataInputModel


router = APIRouter()

@router.post("/delete")
def delete_image(request:Request):
    userId = request.query_params.get("userId")
    timestamp = request.query_params.get("timestamp")
    try:
        md = Metadata(userId=userId)
        image = md.delete_item(itemInfo=MetadataInputModel(
            userId=userId,
            timestamp=timestamp
        ))
        return Response(
            content="Successfully delete image",
            status_code=200
        )
    except Exception as e:
        return Response(
            content=f"Failed to fetch: {e}",
            status_code=500
        )