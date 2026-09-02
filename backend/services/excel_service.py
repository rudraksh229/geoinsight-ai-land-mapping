import os
import pandas as pd
from sqlalchemy.orm import Session
from models import Report


def export_excel(db: Session):

    reports = db.query(Report).all()

    data = []

    for report in reports:
        data.append({
            "Latitude": report.latitude,
            "Longitude": report.longitude,
            "Radius": report.radius,
            "Vegetation": report.vegetation,
            "Water": report.water,
            "Built-up": report.builtup,
            "Barren": report.barren,
            "Suitability Score": report.suitability_score,
            "Created At": report.created_at
        })

    os.makedirs("exports", exist_ok=True)

    filename = "exports/reports.xlsx"

    df = pd.DataFrame(data)

    df.to_excel(filename, index=False)

    return filename
