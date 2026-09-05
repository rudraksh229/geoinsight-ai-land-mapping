
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user

from services.csv_service import export_csv


router = APIRouter(
    prefix="/export",
    tags=["CSV Export"],
)


@router.get("/csv")
def download_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate and download a CSV report
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

        filename = export_csv(
            db=db,
            user_id=int(user_id),
        )

        return FileResponse(
            path=filename,
            media_type="text/csv",
            filename="GeoInsight_Reports.csv",
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
            f"[CSV Export Router] "
            f"CSV export error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate CSV report. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
