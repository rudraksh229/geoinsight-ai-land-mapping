from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from schemas import PDFRequest
from services.pdf_service import generate_pdf
from security import get_current_user

router = APIRouter(
    prefix="/pdf",
    tags=["PDF Report"]
)


@router.post("/generate")
def create_pdf(
    request: PDFRequest,
    current_user=Depends(get_current_user)
):

    pdf = generate_pdf(request.model_dump())

    return FileResponse(
        path=pdf,
        filename="GeoInsight_Report.pdf",
        media_type="application/pdf"
    )
