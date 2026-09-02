from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from security import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# DASHBOARD STATS
# ============================================================

@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analyses = (
        db.query(models.Analysis)
        .filter(models.Analysis.user_id == current_user.id)
        .order_by(models.Analysis.id.desc())
        .all()
    )

    if not analyses:
        return {
            "hasData": False,
            "totalArea": "0 Ha",
            "barrenLand": "0 Ha",
            "vegetation": "0 Ha",
            "agriculturalLand": "0 Ha",
            "waterBodies": "0 Ha",
            "urbanLand": "0 Ha",
            "aiConfidence": "—",
            "trends": {
                "totalArea": None,
                "barrenLand": None,
                "vegetation": None,
                "agriculturalLand": None,
                "waterBodies": None,
                "aiConfidence": None
            }
        }

    total_area = sum(
        analysis.total_area or 0
        for analysis in analyses
    )

    vegetation_area = sum(
        analysis.vegetation or 0
        for analysis in analyses
    )

    agriculture_area = sum(
        analysis.agriculture or 0
        for analysis in analyses
    )

    water_area = sum(
        analysis.water or 0
        for analysis in analyses
    )

    builtup_area = sum(
        analysis.builtup or 0
        for analysis in analyses
    )

    barren_area = sum(
        analysis.barren or 0
        for analysis in analyses
    )

    confidence_values = [
        analysis.confidence
        for analysis in analyses
        if analysis.confidence is not None
    ]

    average_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values
        else 0
    )

    return {
        "hasData": True,
        "totalArea": f"{total_area:.2f} Ha",
        "barrenLand": f"{barren_area:.2f} Ha",
        "vegetation": f"{vegetation_area:.2f} Ha",
        "agriculturalLand": f"{agriculture_area:.2f} Ha",
        "waterBodies": f"{water_area:.2f} Ha",
        "urbanLand": f"{builtup_area:.2f} Ha",
        "aiConfidence": f"{average_confidence:.2f}%",
        "trends": {
            "totalArea": None,
            "barrenLand": None,
            "vegetation": None,
            "agriculturalLand": None,
            "waterBodies": None,
            "aiConfidence": None
        }
    }


# ============================================================
# DASHBOARD CHARTS
# ============================================================

@router.get("/charts")
def dashboard_charts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analyses = (
        db.query(models.Analysis)
        .filter(models.Analysis.user_id == current_user.id)
        .order_by(models.Analysis.id.desc())
        .all()
    )

    if not analyses:
        return {
            "hasData": False,
            "pieChart": {
                "labels": [],
                "data": [],
                "backgroundColor": []
            },
            "barChart": {
                "labels": [],
                "vegetation": [],
                "agriculture": [],
                "barren": [],
                "urban": [],
                "water": []
            }
        }

    vegetation = sum(
        analysis.vegetation or 0
        for analysis in analyses
    )

    agriculture = sum(
        analysis.agriculture or 0
        for analysis in analyses
    )

    barren = sum(
        analysis.barren or 0
        for analysis in analyses
    )

    urban = sum(
        analysis.builtup or 0
        for analysis in analyses
    )

    water = sum(
        analysis.water or 0
        for analysis in analyses
    )

    vegetation = round(vegetation, 2)
    agriculture = round(agriculture, 2)
    barren = round(barren, 2)
    urban = round(urban, 2)
    water = round(water, 2)

    pie_data = [
        vegetation,
        agriculture,
        barren,
        urban,
        water
    ]

    has_classification_data = any(
        value > 0
        for value in pie_data
    )

    if not has_classification_data:
        return {
            "hasData": False,
            "pieChart": {
                "labels": [],
                "data": [],
                "backgroundColor": []
            },
            "barChart": {
                "labels": [],
                "vegetation": [],
                "agriculture": [],
                "barren": [],
                "urban": [],
                "water": []
            }
        }

    return {
        "hasData": True,
        "pieChart": {
            "labels": [
                "Vegetation",
                "Agricultural Land",
                "Barren Land",
                "Urban Land",
                "Water Bodies"
            ],
            "data": pie_data,
            "backgroundColor": [
                "#22c55e",
                "#eab308",
                "#a16207",
                "#6b7280",
                "#3b82f6"
            ]
        },
        "barChart": {
            "labels": [
                "Analyzed Area"
            ],
            "vegetation": [
                vegetation
            ],
            "agriculture": [
                agriculture
            ],
            "barren": [
                barren
            ],
            "urban": [
                urban
            ],
            "water": [
                water
            ]
        }
    }