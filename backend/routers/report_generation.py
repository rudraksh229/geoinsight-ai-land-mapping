
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database import get_db
from schemas import ReportCreate
from security import get_current_user

from services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def get_user_id(current_user) -> int:
    """
    Safely extract authenticated user's ID.
    """
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        user_id = getattr(current_user, "id", None)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is missing.",
        )

    return int(user_id)


@router.post("/")
def save_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user_id = get_user_id(current_user)

        return ReportService.create_report(
            report=report,
            db=db,
            user_id=user_id,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"[Report Generation] Create report error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report. Reason: {str(exc)}",
        ) from exc


@router.get("/")
def list_reports(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user_id = get_user_id(current_user)

        return ReportService.get_all_reports(
            db=db,
            user_id=user_id,
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(f"[Report Generation] List reports error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch reports. Reason: {str(exc)}",
        ) from exc


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user_id = get_user_id(current_user)

        report = ReportService.get_report(
            report_id=report_id,
            db=db,
            user_id=user_id,
        )

        if report is None:
            raise HTTPException(
                status_code=404,
                detail="Report not found.",
            )

        return report

    except HTTPException:
        raise

    except Exception as exc:
        print(f"[Report Generation] Get report error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch report. Reason: {str(exc)}",
        ) from exc


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user_id = get_user_id(current_user)

        result = ReportService.delete_report(
            report_id=report_id,
            db=db,
            user_id=user_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Report not found.",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        print(f"[Report Generation] Delete report error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report. Reason: {str(exc)}",
        ) from exc