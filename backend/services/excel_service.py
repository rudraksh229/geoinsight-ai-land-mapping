import os
import pandas as pd
from pymongo.database import Database

from models import Analysis


def export_excel(
    db: Database,
    user_id: int,
):
    """
    Export analysis records for the authenticated user
    as an Excel file.
    """
    docs = list(
        db["analysis"]
        .find({"user_id": int(user_id)})
        .sort("created_at", -1)
    )
    analyses = [Analysis.from_doc(d) for d in docs]

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

    os.makedirs("exports", exist_ok=True)
    filename = os.path.join("exports", "reports.xlsx")

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

    return filename
