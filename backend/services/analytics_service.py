
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Analysis


def get_dashboard_summary(
    db: Session,
    user_id: int,
):
    """
    Generate analytics summary for the authenticated user.
    """

    reports = (
        db.query(Analysis)
        .filter(
            Analysis.user_id == user_id
        )
        .all()
    )

    total_reports = len(reports)

    total_vegetation = sum(
        r.vegetation or 0
        for r in reports
    )

    total_water = sum(
        r.water or 0
        for r in reports
    )

    total_builtup = sum(
        r.builtup or 0
        for r in reports
    )

    total_barren = sum(
        r.barren or 0
        for r in reports
    )

    average_confidence = (
        db.query(
            func.avg(
                Analysis.confidence
            )
        )
        .filter(
            Analysis.user_id == user_id
        )
        .scalar()
        or 0
    )

    latest_analysis = (
        db.query(Analysis)
        .filter(
            Analysis.user_id == user_id
        )
        .order_by(
            Analysis.created_at.desc()
        )
        .first()
    )

    return {
        "total_reports": total_reports,

        "landcover": {
            "vegetation": round(
                total_vegetation,
                2,
            ),
            "water": round(
                total_water,
                2,
            ),
            "builtup": round(
                total_builtup,
                2,
            ),
            "barren": round(
                total_barren,
                2,
            ),
        },

        "average_confidence": round(
            float(average_confidence),
            2,
        ),

        "latest_analysis": {
            "id": (
                latest_analysis.id
                if latest_analysis
                else None
            ),

            "created_at": (
                latest_analysis.created_at
                if latest_analysis
                else None
            ),

            "village": (
                latest_analysis.village
                if latest_analysis
                else None
            ),

            "district": (
                latest_analysis.district
                if latest_analysis
                else None
            ),

            "state": (
                latest_analysis.state
                if latest_analysis
                else None
            ),
        },
    }
