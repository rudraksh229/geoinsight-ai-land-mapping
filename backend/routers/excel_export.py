
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user

from services.excel_service import export_excel


router = APIRouter(
    prefix="/export",
    tags=["Excel Export"],
)


@router.get("/excel")
def download_excel(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate and download an Excel report
    for the authenticated user.
    """

    try:
        user_id = getattr(
            current_user,
            "id",
            None,
        )

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Authenticated user information is missing.",
            )

        filename = export_excel(
            db=db,
            user_id=int(user_id),
        )

        return FileResponse(
            path=filename,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            filename="GeoInsight_Reports.xlsx",
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Excel Export Router] "
            f"Excel export error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate Excel report. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
