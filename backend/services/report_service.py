from sqlalchemy.orm import Session
import models
import schemas


class ReportService:

    @staticmethod
    def get_all_reports(
        db: Session,
        user_id: int
    ):
        return (
            db.query(models.Analysis)
            .filter(
                models.Analysis.user_id == user_id
            )
            .order_by(
                models.Analysis.id.desc()
            )
            .all()
        )

    @staticmethod
    def get_report(
        report_id: int,
        db: Session,
        user_id: int
    ):
        return (
            db.query(models.Analysis)
            .filter(
                models.Analysis.id == report_id,
                models.Analysis.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def create_report(
        analysis: schemas.AnalysisCreate,
        db: Session,
        user_id: int
    ):

        db_analysis = models.Analysis(

            user_id=user_id,

            village=analysis.village,
            district=analysis.district,
            state=analysis.state,

            date=analysis.date,

            total_area=analysis.total_area,
            mapped_area=analysis.mapped_area,

            confidence=analysis.confidence,

            status=analysis.status
        )

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return db_analysis

    @staticmethod
    def delete_report(
        report_id: int,
        db: Session,
        user_id: int
    ):

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
        