import math
from datetime import datetime
from sqlalchemy.orm import Session
import models

class ReportService:

    @staticmethod
    def _safe_float(value, default=0.0):
        if value is None:
            return default
        try:
            val = float(value)
            if math.isnan(val) or math.isinf(val):
                return default
            return val
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _to_dict(report):
        if not report:
            return None

        # Direct Database Raw Values Extraction
        total = ReportService._safe_float(getattr(report, "total_area", 0.0), 0.0)
        mapped = ReportService._safe_float(getattr(report, "mapped_area", 0.0), total)
        
        veg = ReportService._safe_float(getattr(report, "vegetation", 0.0), 0.0)
        agri = ReportService._safe_float(getattr(report, "agriculture", 0.0), 0.0)
        built = ReportService._safe_float(getattr(report, "builtup", 0.0), 0.0)
        barren = ReportService._safe_float(getattr(report, "barren", 0.0), 0.0)
        water = ReportService._safe_float(getattr(report, "water", 0.0), 0.0)
        conf = ReportService._safe_float(getattr(report, "confidence", 0.0), 0.0)

        # Date formatting
        raw_date = getattr(report, "date", None) or getattr(report, "created_at", None)
        if isinstance(raw_date, datetime):
            formatted_date = raw_date.strftime("%Y-%m-%d")
        elif raw_date:
            formatted_date = str(raw_date).split("T")[0]
        else:
            formatted_date = datetime.now().strftime("%Y-%m-%d")

        raw_status = getattr(report, "status", None)
        status_str = "Completed" if not raw_status or str(raw_status).strip() in ["None", "null", ""] else str(raw_status)

        return {
            "id": report.id,
            "reportId": f"#{report.id}",
            "user_id": getattr(report, "user_id", 1),
            "village": getattr(report, "village", "-") or "-",
            "district": getattr(report, "district", "-") or "-",
            "state": getattr(report, "state", "-") or "-",
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
        reports = db.query(models.Analysis).filter(models.Analysis.user_id == user_id).order_by(models.Analysis.id.desc()).all()
        if not reports:
            reports = db.query(models.Analysis).order_by(models.Analysis.id.desc()).all()
        return [ReportService._to_dict(r) for r in reports]

    @staticmethod
    def get_report(report_id: int, db: Session, user_id: int):
        report = db.query(models.Analysis).filter(models.Analysis.id == report_id).first()
        return ReportService._to_dict(report)

    @staticmethod
    def create_report(analysis, db: Session, user_id: int):
        data = analysis.dict() if hasattr(analysis, "dict") else analysis

        # Extract Original Calculated Values From Request Payload Flexibly
        land_cover = data.get("landCover") or data.get("land_cover") or {}
        
        total = ReportService._safe_float(data.get("total_area") or data.get("totalArea"), 0.0)
        mapped = ReportService._safe_float(data.get("mapped_area") or data.get("mappedArea"), total)

        veg = ReportService._safe_float(data.get("vegetation") or land_cover.get("vegetation"), 0.0)
        agri = ReportService._safe_float(data.get("agriculture") or land_cover.get("agriculture"), 0.0)
        water = ReportService._safe_float(data.get("water") or land_cover.get("water"), 0.0)
        built = ReportService._safe_float(data.get("builtup") or data.get("built_up") or land_cover.get("builtup"), 0.0)
        barren = ReportService._safe_float(data.get("barren") or land_cover.get("barren"), 0.0)
        conf = ReportService._safe_float(data.get("confidence") or data.get("aiConfidence"), 0.0)

        db_analysis = models.Analysis(
            user_id=user_id,
            village=data.get("village"),
            district=data.get("district"),
            state=data.get("state"),
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            total_area=total,
            mapped_area=mapped,
            vegetation=veg,
            agriculture=agri,
            water=water,
            builtup=built,
            barren=barren,
            confidence=conf,
            status="Completed"
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return ReportService._to_dict(db_analysis)

    @staticmethod
    def delete_report(report_id: int, db: Session, user_id: int):
        report = db.query(models.Analysis).filter(models.Analysis.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
        return report
