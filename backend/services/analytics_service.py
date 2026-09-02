from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Report


def get_dashboard_summary(db: Session):

    reports = db.query(Report).all()

    total_reports = len(reports)

    total_vegetation = sum(r.vegetation or 0 for r in reports)
    total_water = sum(r.water or 0 for r in reports)
    total_builtup = sum(r.builtup or 0 for r in reports)
    total_barren = sum(r.barren or 0 for r in reports)

    avg_score = (
        db.query(func.avg(Report.suitability_score)).scalar()
        or 0
    )

    latest_report = (
        db.query(Report)
        .order_by(Report.created_at.desc())
        .first()
    )

    return {

        "total_reports": total_reports,

        "landcover": {

            "vegetation": round(total_vegetation, 2),
            "water": round(total_water, 2),
            "builtup": round(total_builtup, 2),
            "barren": round(total_barren, 2)

        },

        "average_suitability_score": round(avg_score, 2),

        "latest_analysis": {

            "id": latest_report.id if latest_report else None,

            "created_at": (
                latest_report.created_at
                if latest_report
                else None
            )

        }

    }
