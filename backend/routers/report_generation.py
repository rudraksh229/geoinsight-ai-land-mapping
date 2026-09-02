from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ReportCreate
from services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/")
def save_report(
    report: ReportCreate,
    db: Session = Depends(get_db)
):
    return ReportService.create_report(report, db)


@router.get("/")
def list_reports(
    db: Session = Depends(get_db)
):
    return ReportService.get_all_reports(db)
