from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import schemas

from database import get_db
from security import get_current_user
from services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# ============================================================
# GET ALL REPORTS
# ============================================================

@router.get("")
def get_reports(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return only reports belonging to the authenticated user.
    """

    return ReportService.get_all_reports(
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# GET SINGLE REPORT
# ============================================================

@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return a single report only if it belongs to
    the authenticated user.
    """

    report = ReportService.get_report(
        report_id=report_id,
        db=db,
        user_id=current_user.id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return report


# ============================================================
# CREATE REPORT
# ============================================================

@router.post("")
def create_report(
    analysis: schemas.AnalysisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new analysis/report for the authenticated user.
    """

    return ReportService.create_report(
        analysis_payload=analysis,
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# DELETE REPORT
# ============================================================

@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a report only if it belongs to
    the authenticated user.
    """

    report = ReportService.delete_report(
        report_id=report_id,
        db=db,
        user_id=current_user.id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return {
        "success": True,
        "message": "Report deleted successfully.",
        "reportId": report_id,
    }
