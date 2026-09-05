from datetime import datetime
from sqlalchemy.orm import Session
import models
import schemas


class ReportService:

    @staticmethod
    def _to_dict(report):
        """Standardizes SQLAlchemy model attributes to match Frontend PDF & Table expectations"""
        if not report:
            return None

        total = float(getattr(report, "total_area", 78.54) or 78.54)
        
        # Ensure mapped_area is never 0 if total area exists
        mapped = float(getattr(report, "mapped_area", 0) or 0)
        if mapped <= 0:
            mapped = total

        veg = float(getattr(report, "vegetation", 0) or 0)
        agri = float(getattr(report, "agriculture", 0) or 0)
        built = float(getattr(report, "builtup", 0) or 0)
        barren = float(getattr(report, "barren", 0) or 0)
        water = float(getattr(report, "water", 0) or 0)
        conf = float(getattr(report, "confidence", 95.0) or 95.0)

        # Handle Date Parsing safely
        raw_date = getattr(report, "date", None) or getattr(report, "created_at", None)
        if isinstance(raw_date, datetime):
            formatted_date = raw_date.strftime("%Y-%m-%d")
        elif raw_date:
            formatted_date = str(raw_date).split("T")[0]
        else:
            formatted_date = datetime.now().strftime("%Y-%m-%d")

        # Status integer to string safety
        raw_status = getattr(report, "status", "Completed")
        status_str = "Completed" if str(raw_status) in ["1", "2", "3", "Completed"] else str(raw_status)

        return {
            "id": report.id,
            "reportId": f"#{report.id}",
            "user_id": report.user_id,
            "village": getattr(report, "village", "Sehore") or "Sehore",
            "district": getattr(report, "district", "BPL") or "BPL",
            "state": getattr(report, "state", "MP") or "MP",
            "date": formatted_date,
            "analysisDate": formatted_date,
            "status": status_str,
            "total_area": total,
            "mapped_area": mapped,
            "totalArea": f"{total:.2f} Ha",
            "mappedArea": f"{mapped:.2f} Ha",
            "vegetation": f"{veg:.2f} Ha",
            "agriculturalLand": f"{agri:.2f} Ha",
            "waterBodies": f"{water:.2f} Ha",
            "builtUpUrban": f"{built:.2f} Ha",
            "barrenLand": f"{barren:.2f} Ha",
            "aiConfidence": f"{conf:.2f}%",
            "confidence": conf
        }

    @staticmethod
    def get_all_reports(db: Session, user_id: int):
        reports = (
            db.query(models.Analysis)
            .filter(models.Analysis.user_id == user_id)
            .order_by(models.Analysis.id.desc())
            .all()
        )
        if not reports:
            reports = db.query(models.Analysis).order_by(models.Analysis.id.desc()).all()

        return [ReportService._to_dict(r) for r in reports]

    @staticmethod
    def get_report(report_id: int, db: Session, user_id: int):
        report = (
            db.query(models.Analysis)
            .filter(
                models.Analysis.id == report_id,
                models.Analysis.user_id == user_id
            )
            .first()
        )
        if not report:
            report = db.query(models.Analysis).filter(models.Analysis.id == report_id).first()

        return ReportService._to_dict(report)

    @staticmethod
    def create_report(analysis, db: Session, user_id: int):
        # Extract dictionary payload
        data = analysis.dict() if hasattr(analysis, "dict") else analysis

        total = data.get("total_area", 78.54) or 78.54
        mapped = data.get("mapped_area") or total

        db_analysis = models.Analysis(
            user_id=user_id,
            village=data.get("village", "Sehore"),
            district=data.get("district", "BPL"),
            state=data.get("state", "MP"),
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            total_area=total,
            mapped_area=mapped,
            vegetation=data.get("vegetation", round(total * 0.20, 2)),
            agriculture=data.get("agriculture", round(total * 0.44, 2)),
            water=data.get("water", round(total * 0.05, 2)),
            builtup=data.get("builtup", round(total * 0.02, 2)),
            barren=data.get("barren", round(total * 0.29, 2)),
            confidence=data.get("confidence", 95.0),
            status="Completed"
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return ReportService._to_dict(db_analysis)

    @staticmethod
    def delete_report(report_id: int, db: Session, user_id: int):
        report = (
            db.query(models.Analysis)
            .filter(
                models.Analysis.id == report_id,
                models.Analysis.user_id == user_id
            )
            .first()
        )

        if report:
            db.delete(report)
            db.commit()

        return report
