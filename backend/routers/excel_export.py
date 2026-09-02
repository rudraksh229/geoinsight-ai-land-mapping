from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from services.excel_service import export_excel

router = APIRouter(
    prefix="/export",
    tags=["Excel Export"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/excel")
def download_excel(db: Session = Depends(get_db)):

    filename = export_excel(db)

    return FileResponse(
        path=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="GeoInsight_Reports.xlsx"
    )
