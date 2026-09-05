from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models

from database import get_db
from security import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# HELPERS
# ============================================================

def get_user_id(current_user) -> int:
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        user_id = getattr(
            current_user,
            "id",
            None,
        )

    if user_id is None:
        raise ValueError(
            "Authenticated user ID is missing."
        )

    return int(user_id)


def empty_dashboard():
    return {
        "hasData": False,

        "totalArea": "0.00 Ha",
        "barrenLand": "0.00 Ha",
        "vegetation": "0.00 Ha",
        "agriculturalLand": "0.00 Ha",
        "waterBodies": "0.00 Ha",
        "urbanLand": "0.00 Ha",

        "aiConfidence": "0.0%",

        "trends": {},
    }


# ============================================================
# DASHBOARD STATS
# ============================================================

@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Calculate dashboard statistics using only the
    authenticated user's analyses.
    """

    user_id = get_user_id(
        current_user
    )

    analyses = (
        db.query(models.Analysis)
        .filter(
            models.Analysis.user_id
            == user_id
        )
        .order_by(
            models.Analysis.id.desc()
        )
        .all()
    )

    if not analyses:
        return empty_dashboard()

    # --------------------------------------------------------
    # Aggregate values
    # --------------------------------------------------------

    total_area = sum(
        float(a.total_area or 0)
        for a in analyses
    )

    vegetation = sum(
        float(a.vegetation or 0)
        for a in analyses
    )

    agriculture = sum(
        float(a.agriculture or 0)
        for a in analyses
    )

    water = sum(
        float(a.water or 0)
        for a in analyses
    )

    builtup = sum(
        float(a.builtup or 0)
        for a in analyses
    )

    barren = sum(
        float(a.barren or 0)
        for a in analyses
    )

    # --------------------------------------------------------
    # Average AI confidence
    # --------------------------------------------------------

    confidence_values = [
        float(a.confidence)
        for a in analyses
        if a.confidence is not None
    ]

    average_confidence = (
        sum(confidence_values)
        / len(confidence_values)
        if confidence_values
        else 0.0
    )

    # --------------------------------------------------------
    # Return dashboard data
    # --------------------------------------------------------

    return {
        "hasData": True,

        "totalArea": (
            f"{total_area:.2f} Ha"
        ),

        "barrenLand": (
            f"{barren:.2f} Ha"
        ),

        "vegetation": (
            f"{vegetation:.2f} Ha"
        ),

        "agriculturalLand": (
            f"{agriculture:.2f} Ha"
        ),

        "waterBodies": (
            f"{water:.2f} Ha"
        ),

        "urbanLand": (
            f"{builtup:.2f} Ha"
        ),

        "aiConfidence": (
            f"{average_confidence:.1f}%"
        ),

        "trends": {},
    }


# ============================================================
# DASHBOARD CHARTS
# ============================================================

@router.get("/charts")
def dashboard_charts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate chart data using only the authenticated
    user's analyses.
    """

    user_id = get_user_id(
        current_user
    )

    analyses = (
        db.query(models.Analysis)
        .filter(
            models.Analysis.user_id
            == user_id
        )
        .order_by(
            models.Analysis.id.desc()
        )
        .all()
    )

    if not analyses:
        return {
            "hasData": False,

            "pieChart": {
                "labels": [],
                "data": [],
                "backgroundColor": [],
            },

            "barChart": {
                "labels": [],
                "vegetation": [],
                "agriculture": [],
                "barren": [],
                "urban": [],
                "water": [],
            },
        }

    # --------------------------------------------------------
    # Overall totals
    # --------------------------------------------------------

    vegetation = round(
        sum(
            float(a.vegetation or 0)
            for a in analyses
        ),
        2,
    )

    agriculture = round(
        sum(
            float(a.agriculture or 0)
            for a in analyses
        ),
        2,
    )

    barren = round(
        sum(
            float(a.barren or 0)
            for a in analyses
        ),
        2,
    )

    urban = round(
        sum(
            float(a.builtup or 0)
            for a in analyses
        ),
        2,
    )

    water = round(
        sum(
            float(a.water or 0)
            for a in analyses
        ),
        2,
    )

    # --------------------------------------------------------
    # Group data by state
    # --------------------------------------------------------

    state_groups = {}

    for analysis in analyses:

        state = (
            getattr(
                analysis,
                "state",
                None,
            )
            or "Unknown"
        )

        if state not in state_groups:
            state_groups[state] = {
                "vegetation": 0.0,
                "agriculture": 0.0,
                "barren": 0.0,
                "urban": 0.0,
                "water": 0.0,
            }

        state_groups[state][
            "vegetation"
        ] += float(
            analysis.vegetation or 0
        )

        state_groups[state][
            "agriculture"
        ] += float(
            analysis.agriculture or 0
        )

        state_groups[state][
            "barren"
        ] += float(
            analysis.barren or 0
        )

        state_groups[state][
            "urban"
        ] += float(
            analysis.builtup or 0
        )

        state_groups[state][
            "water"
        ] += float(
            analysis.water or 0
        )

    states = list(
        state_groups.keys()
    )

    # --------------------------------------------------------
    # Chart response
    # --------------------------------------------------------

    return {
        "hasData": True,

        "pieChart": {
            "labels": [
                "Vegetation",
                "Agricultural Land",
                "Barren Land",
                "Urban Land",
                "Water Bodies",
            ],

            "data": [
                vegetation,
                agriculture,
                barren,
                urban,
                water,
            ],

            "backgroundColor": [
                "#22c55e",
                "#eab308",
                "#a16207",
                "#6b7280",
                "#3b82f6",
            ],
        },

        "barChart": {
            "labels": states,

            "vegetation": [
                round(
                    state_groups[state][
                        "vegetation"
                    ],
                    2,
                )
                for state in states
            ],

            "agriculture": [
                round(
                    state_groups[state][
                        "agriculture"
                    ],
                    2,
                )
                for state in states
            ],

            "barren": [
                round(
                    state_groups[state][
                        "barren"
                    ],
                    2,
                )
                for state in states
            ],

            "urban": [
                round(
                    state_groups[state][
                        "urban"
                    ],
                    2,
                )
                for state in states
            ],

            "water": [
                round(
                    state_groups[state][
                        "water"
                    ],
                    2,
                )
                for state in states
            ],
        },
    }
