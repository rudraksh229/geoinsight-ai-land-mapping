from sqlalchemy.orm import Session
import models


class DashboardService:

    @staticmethod
    def get_dashboard_stats(db: Session):

        analyses = db.query(models.Analysis).all()

        total_area = sum(a.total_area or 0 for a in analyses)
        mapped_area = sum(a.mapped_area or 0 for a in analyses)

        avg_confidence = (
            sum(a.confidence or 0 for a in analyses) / len(analyses)
            if analyses else 0
        )

        return {
            "totalArea": f"{total_area:.2f} Ha",
            "mappedArea": f"{mapped_area:.2f} Ha",
            "barrenLand": f"{max(total_area - mapped_area, 0):.2f} Ha",
            "totalReports": len(analyses),
            "aiConfidence": f"{avg_confidence:.2f}%"
        }

    @staticmethod
    def get_dashboard_charts(db: Session):

        analyses = db.query(models.Analysis).all()

        mapped = sum(a.mapped_area or 0 for a in analyses)

        vegetation = mapped * 0.40
        agriculture = mapped * 0.30
        barren = mapped * 0.17
        urban = mapped * 0.08
        water = mapped * 0.05

        return {
            "pieChart": {
                "labels": [
                    "Vegetation",
                    "Agriculture",
                    "Barren",
                    "Urban",
                    "Water"
                ],
                "data": [
                    vegetation,
                    agriculture,
                    barren,
                    urban,
                    water
                ]
            },
            "barChart": {
                "labels": ["Mapped Area"],
                "vegetation": [vegetation],
                "agriculture": [agriculture],
                "barren": [barren],
                "urban": [urban],
                "water": [water]
            }
        }
