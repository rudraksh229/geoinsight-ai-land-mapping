from pymongo.database import Database
from models import Analysis


def get_dashboard_summary(
    db: Database,
    user_id: int,
):
    """
    Generate analytics summary for the authenticated user.
    """
    docs = list(
        db["analysis"]
        .find({"user_id": int(user_id)})
        .sort("created_at", -1)
    )

    reports = [Analysis.from_doc(d) for d in docs]
    total_reports = len(reports)

    total_vegetation = sum(r.vegetation or 0 for r in reports)
    total_water = sum(r.water or 0 for r in reports)
    total_builtup = sum(r.builtup or 0 for r in reports)
    total_barren = sum(r.barren or 0 for r in reports)

    confidences = [
        float(r.confidence)
        for r in reports
        if r.confidence is not None
    ]
    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    latest_analysis = reports[0] if reports else None

    return {
        "total_reports": total_reports,
        "landcover": {
            "vegetation": round(total_vegetation, 2),
            "water": round(total_water, 2),
            "builtup": round(total_builtup, 2),
            "barren": round(total_barren, 2),
        },
        "average_confidence": round(float(average_confidence), 2),
        "latest_analysis": {
            "id": latest_analysis.id if latest_analysis else None,
            "created_at": latest_analysis.created_at if latest_analysis else None,
            "village": latest_analysis.village if latest_analysis else None,
            "district": latest_analysis.district if latest_analysis else None,
            "state": latest_analysis.state if latest_analysis else None,
        },
    }
