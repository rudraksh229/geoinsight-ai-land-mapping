import math
from datetime import datetime
from pymongo.database import Database

from database import get_next_sequence
import models


class ReportService:

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_float(value, fallback=0.0):
        if value is None:
            return fallback

        try:
            parsed = float(value)
            if math.isnan(parsed) or math.isinf(parsed):
                return fallback
            return parsed
        except (ValueError, TypeError):
            return fallback

    @staticmethod
    def _safe_user_id(user_id):
        if user_id is None:
            return None

        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _format_data(analysis):
        if not analysis:
            return None

        if isinstance(analysis, dict):
            analysis = models.Analysis.from_doc(analysis)

        total = ReportService._safe_float(
            getattr(analysis, "total_area", None),
            0.0,
        )
        mapped = ReportService._safe_float(
            getattr(analysis, "mapped_area", None),
            total,
        )
        vegetation = ReportService._safe_float(
            getattr(analysis, "vegetation", None),
            0.0,
        )
        agriculture = ReportService._safe_float(
            getattr(analysis, "agriculture", None),
            0.0,
        )
        water = ReportService._safe_float(
            getattr(analysis, "water", None),
            0.0,
        )
        builtup = ReportService._safe_float(
            getattr(analysis, "builtup", None),
            0.0,
        )
        barren = ReportService._safe_float(
            getattr(analysis, "barren", None),
            0.0,
        )
        confidence = ReportService._safe_float(
            getattr(analysis, "confidence", None),
            0.0,
        )

        raw_date = (
            getattr(analysis, "date", None)
            or getattr(analysis, "created_at", None)
        )

        if isinstance(raw_date, datetime):
            date_string = raw_date.strftime("%Y-%m-%d")
        elif raw_date:
            date_string = str(raw_date).split("T")[0]
        else:
            date_string = datetime.utcnow().strftime("%Y-%m-%d")

        return {
            "id": analysis.id,
            "reportId": f"REP-{analysis.id}",
            "user_id": getattr(analysis, "user_id", None),
            "village": getattr(analysis, "village", None) or "Unknown",
            "district": getattr(analysis, "district", None) or "Unknown",
            "state": getattr(analysis, "state", None) or "Unknown",
            "latitude": getattr(analysis, "latitude", None),
            "longitude": getattr(analysis, "longitude", None),
            "radius": getattr(analysis, "radius", None),
            "date": date_string,
            "analysisDate": date_string,
            "status": getattr(analysis, "status", None) or "Completed",

            # Numeric values
            "total_area": total,
            "mapped_area": mapped,
            "vegetation_num": vegetation,
            "agriculture_num": agriculture,
            "water_num": water,
            "builtup_num": builtup,
            "barren_num": barren,
            "confidence": confidence,

            # Formatted values for existing frontend
            "totalArea": f"{total:.2f} Ha",
            "mappedArea": f"{mapped:.2f} Ha",
            "vegetation": f"{vegetation:.2f} Ha",
            "agriculturalLand": f"{agriculture:.2f} Ha",
            "waterBodies": f"{water:.2f} Ha",
            "builtUpUrban": f"{builtup:.2f} Ha",
            "barrenLand": f"{barren:.2f} Ha",
            "aiConfidence": f"{confidence:.2f}%",

            "stats": {
                "totalArea": total,
                "mappedArea": mapped,
                "vegetation": vegetation,
                "agriculturalLand": agriculture,
                "waterBodies": water,
                "builtUpUrban": builtup,
                "barrenLand": barren,
                "confidence": confidence,
            },
        }

    # ========================================================
    # GET ALL REPORTS
    # ========================================================

    @staticmethod
    def get_all_reports(
        db: Database,
        user_id=None,
    ):
        safe_user_id = ReportService._safe_user_id(user_id)

        if safe_user_id is None:
            return []

        try:
            docs = list(
                db["analysis"]
                .find({"user_id": safe_user_id})
                .sort("id", -1)
            )

            return [
                ReportService._format_data(doc)
                for doc in docs
            ]

        except Exception as exc:
            print(f"[ReportService] Get reports error: {exc}")
            raise

    # ========================================================
    # GET SINGLE REPORT
    # ========================================================

    @staticmethod
    def get_report(
        report_id: int,
        db: Database,
        user_id=None,
    ):
        safe_user_id = ReportService._safe_user_id(user_id)

        if safe_user_id is None:
            return None

        try:
            doc = db["analysis"].find_one({
                "id": int(report_id),
                "user_id": safe_user_id,
            })

            return ReportService._format_data(doc)

        except Exception as exc:
            print(f"[ReportService] Get report error: {exc}")
            raise

    # ========================================================
    # CREATE REPORT
    # ========================================================

    @staticmethod
    def create_report(
        analysis_payload,
        db: Database,
        user_id=None,
    ):
        safe_user_id = ReportService._safe_user_id(user_id)

        if safe_user_id is None:
            raise ValueError(
                "A valid authenticated user ID is required."
            )

        if hasattr(analysis_payload, "model_dump"):
            data = analysis_payload.model_dump()
        elif hasattr(analysis_payload, "dict"):
            data = analysis_payload.dict()
        elif isinstance(analysis_payload, dict):
            data = analysis_payload
        else:
            raise ValueError("Invalid analysis payload.")

        total_area = (
            data.get("total_area")
            if data.get("total_area") is not None
            else data.get("totalArea")
        )
        mapped_area = (
            data.get("mapped_area")
            if data.get("mapped_area") is not None
            else data.get("mappedArea")
        )

        vegetation = data.get("vegetation")
        agriculture = data.get("agriculture")
        water = data.get("water")
        builtup = data.get("builtup")
        barren = data.get("barren")
        confidence = data.get("confidence")

        land_cover = (
            data.get("landCover")
            or data.get("land_cover")
            or {}
        )

        if vegetation is None:
            vegetation = land_cover.get("vegetation")
        if agriculture is None:
            agriculture = land_cover.get("agriculture")
        if water is None:
            water = land_cover.get("water")
        if builtup is None:
            builtup = land_cover.get("builtup")
        if barren is None:
            barren = land_cover.get("barren")
        if confidence is None:
            confidence = data.get("aiConfidence")

        now = datetime.utcnow()
        new_id = get_next_sequence("analysis")

        analysis = models.Analysis(
            id=new_id,
            user_id=safe_user_id,
            village=data.get("village", "Unknown"),
            district=data.get("district", "Unknown"),
            state=data.get("state", "Unknown"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            radius=data.get("radius"),
            date=now,
            total_area=ReportService._safe_float(total_area),
            mapped_area=ReportService._safe_float(
                mapped_area,
                ReportService._safe_float(total_area),
            ),
            vegetation=ReportService._safe_float(vegetation),
            agriculture=ReportService._safe_float(agriculture),
            water=ReportService._safe_float(water),
            builtup=ReportService._safe_float(builtup),
            barren=ReportService._safe_float(barren),
            confidence=ReportService._safe_float(confidence),
            status="Completed",
            created_at=now,
        )

        try:
            db["analysis"].insert_one(analysis.to_dict())
            return ReportService._format_data(analysis)
        except Exception as exc:
            print(f"[ReportService] Create report error: {exc}")
            raise

    # ========================================================
    # DELETE REPORT
    # ========================================================

    @staticmethod
    def delete_report(
        report_id: int,
        db: Database,
        user_id=None,
    ):
        safe_user_id = ReportService._safe_user_id(user_id)

        if safe_user_id is None:
            return None

        try:
            doc = db["analysis"].find_one({
                "id": int(report_id),
                "user_id": safe_user_id,
            })

            if doc is None:
                return None

            db["analysis"].delete_one({
                "id": int(report_id),
                "user_id": safe_user_id,
            })

            return models.Analysis.from_doc(doc)

        except Exception as exc:
            print(f"[ReportService] Delete report error: {exc}")
            raise
