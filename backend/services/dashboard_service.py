
from sqlalchemy.orm import Session

import models


class DashboardService:

    @staticmethod
    def get_dashboard_stats(
        db: Session,
        user_id: int,
    ):
        """
        Return dashboard statistics for the authenticated user.
        """

        analyses = (
            db.query(models.Analysis)
            .filter(
                models.Analysis.user_id == user_id
            )
            .all()
        )

        total_area = sum(
            a.total_area or 0
            for a in analyses
        )

        mapped_area = sum(
            a.mapped_area or 0
            for a in analyses
        )

        avg_confidence = (
            sum(
                a.confidence or 0
                for a in analyses
            ) / len(analyses)
            if analyses
            else 0
        )

        total_barren = sum(
            a.barren or 0
            for a in analyses
        )

        return {
            "totalArea": f"{total_area:.2f} Ha",

            "mappedArea": f"{mapped_area:.2f} Ha",

            "barrenLand": f"{total_barren:.2f} Ha",

            "totalReports": len(analyses),

            "aiConfidence": f"{avg_confidence:.2f}%",

            "vegetation": f"{sum(a.vegetation or 0 for a in analyses):.2f} Ha",

            "agriculture": f"{sum(a.agriculture or 0 for a in analyses):.2f} Ha",

            "waterBodies": f"{sum(a.water or 0 for a in analyses):.2f} Ha",

            "urbanLand": f"{sum(a.builtup or 0 for a in analyses):.2f} Ha",
        }

    @staticmethod
    def get_dashboard_charts(
        db: Session,
        user_id: int,
    ):
        """
        Return actual land-cover statistics for the
        authenticated user instead of hardcoded percentages.
        """

        analyses = (
            db.query(models.Analysis)
            .filter(
                models.Analysis.user_id == user_id
            )
            .all()
        )

        vegetation = sum(
            a.vegetation or 0
            for a in analyses
        )

        agriculture = sum(
            a.agriculture or 0
            for a in analyses
        )

        barren = sum(
            a.barren or 0
            for a in analyses
        )

        urban = sum(
            a.builtup or 0
            for a in analyses
        )

        water = sum(
            a.water or 0
            for a in analyses
        )

        return {
            "pieChart": {
                "labels": [
                    "Vegetation",
                    "Agriculture",
                    "Barren",
                    "Urban",
                    "Water",
                ],
                "data": [
                    round(vegetation, 2),
                    round(agriculture, 2),
                    round(barren, 2),
                    round(urban, 2),
                    round(water, 2),
                ],
            },

            "barChart": {
                "labels": [
                    "Mapped Area"
                ],
                "vegetation": [
                    round(vegetation, 2)
                ],
                "agriculture": [
                    round(agriculture, 2)
                ],
                "barren": [
                    round(barren, 2)
                ],
                "urban": [
                    round(urban, 2)
                ],
                "water": [
                    round(water, 2)
                ],
            },
        }
