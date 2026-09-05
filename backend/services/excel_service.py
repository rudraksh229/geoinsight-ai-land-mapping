
import os

import pandas as pd
from sqlalchemy.orm import Session

from models import Analysis


def export_excel(
    db: Session,
    user_id: int,
):
    """
    Export analysis records for the authenticated user
    as an Excel file.
    """

    analyses = (
        db.query(Analysis)
        .filter(
            Analysis.user_id == user_id
        )
        .order_by(
            Analysis.created_at.desc()
        )
        .all()
    )

    data = []

    for analysis in analyses:
        data.append({
            "ID": analysis.id,
            "Village": analysis.village,
            "District": analysis.district,
            "State": analysis.state,
            "Latitude": analysis.latitude,
            "Longitude": analysis.longitude,
            "Radius": analysis.radius,
            "Date": analysis.date,
            "Total Area": analysis.total_area,
            "Mapped Area": analysis.mapped_area,
            "Vegetation": analysis.vegetation,
            "Agriculture": analysis.agriculture,
            "Water": analysis.water,
            "Built-up": analysis.builtup,
            "Barren": analysis.barren,
            "Confidence": analysis.confidence,
            "Status": analysis.status,
            "Created At": analysis.created_at,
        })

    os.makedirs(
        "exports",
        exist_ok=True,
    )

    filename = os.path.join(
        "exports",
        "reports.xlsx",
    )

    df = pd.DataFrame(data)

    df.to_excel(
        filename,
        index=False,
    )

    return filename
