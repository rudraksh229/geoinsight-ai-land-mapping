from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.report_service import ReportService
from security import get_current_user
import schemas


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("")
def get_reports(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return ReportService.get_all_reports(
        db,
        current_user.id
    )


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    report = ReportService.get_report(
        report_id,
        db,
        current_user.id
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


@router.post("")
def create_report(
    analysis: schemas.AnalysisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return ReportService.create_report(
        analysis,
        db,
        current_user.id
    )


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    report = ReportService.delete_report(
        report_id,
        db,
        current_user.id
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return {
        "message": "Report deleted successfully."
    }
    