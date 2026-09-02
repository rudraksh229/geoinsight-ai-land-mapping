from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from services.csv_service import export_csv

router = APIRouter(
    prefix="/export",
    tags=["CSV Export"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/csv")
def download_csv(db: Session = Depends(get_db)):

    filename = export_csv(db)

    return FileResponse(
        filename,
        media_type="text/csv",
        filename="GeoInsight_Reports.csv"
    )
