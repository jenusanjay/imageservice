from fastapi import FastAPI

from imageservice.routes import list_images,delete_image,view_image,home,upload_image

app = FastAPI(
    title= "ImageService API",
    description= "API to be used to upload, list, view/download and delete image",
    version='0.1'
)

app.include_router(home.router)
app.include_router(upload_image.router)
app.include_router(list_images.router)
app.include_router(delete_image.router)
app.include_router(view_image.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="localhost", port=8000,reload=True)

