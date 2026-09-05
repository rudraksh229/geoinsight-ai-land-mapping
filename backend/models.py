from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from database import Base
from datetime import datetime


# =========================================================
# LAND ANALYSIS
# =========================================================

class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,  # Set to True so background guest saves don't fail
        index=True
    )

    village = Column(String, nullable=True, default="Amer")
    district = Column(String, nullable=True, default="JPR")
    state = Column(String, nullable=True, default="RJ")

    # Fixed: Standardized to handle both String and DateTime gracefully
    date = Column(String, nullable=True, default=lambda: datetime.utcnow().strftime("%Y-%m-%d"))

    total_area = Column(Float, default=78.54)
    mapped_area = Column(Float, default=78.54)

    # Land breakdown fields with exact defaults
    vegetation = Column(Float, default=0.0)
    agriculture = Column(Float, default=0.0)
    water = Column(Float, default=0.0)
    builtup = Column(Float, default=0.0)
    barren = Column(Float, default=0.0)

    confidence = Column(Float, default=97.93)
    status = Column(String, default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================================================
# REPORTS
# =========================================================

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)

    vegetation = Column(Float, default=0.0)
    water = Column(Float, default=0.0)
    builtup = Column(Float, default=0.0)
    barren = Column(Float, default=0.0)

    suitability_score = Column(Float, default=0.0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# USERS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="user"
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
