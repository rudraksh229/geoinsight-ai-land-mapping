from fastapi import APIRouter, UploadFile, File

from services.polygon_service import analyze_polygon

router = APIRouter(
    prefix="/polygon",
    tags=["Polygon Analysis"]
)


@router.post("/upload")
async def upload_polygon(
    file: UploadFile = File(...)
):

    contents = await file.read()

    return analyze_polygon(contents)
