import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from schemas import PDFRequest
from services.pdf_service import generate_pdf
from security import get_current_user


router = APIRouter(
    prefix="/pdf",
    tags=["PDF Report"],
)


@router.post("/generate")
def create_pdf(
    request: PDFRequest,
    current_user=Depends(get_current_user),
):
    """
    Generate and return a GeoInsight AI PDF report
    for the authenticated user.
    """

    try:
        data = request.model_dump()

        pdf_path = generate_pdf(
            data
        )

        if not pdf_path:
            raise RuntimeError(
                "PDF generation returned an empty file path."
            )

        if not os.path.isfile(
            pdf_path
        ):
            raise RuntimeError(
                "Generated PDF file was not found."
            )

        return FileResponse(
            path=pdf_path,
            filename="GeoInsight_Report.pdf",
            media_type="application/pdf",
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(
            f"[PDF Router] PDF generation error: {exc}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to generate PDF report. "
                f"Reason: {str(exc)}"
            ),
        )
