from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        default="user",
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    village = Column(
        String,
        nullable=True,
        default="Amer",
    )

    district = Column(
        String,
        nullable=True,
        default="JPR",
    )

    state = Column(
        String,
        nullable=True,
        default="RJ",
    )

    latitude = Column(
        Float,
        nullable=True,
    )

    longitude = Column(
        Float,
        nullable=True,
    )

    radius = Column(
        Float,
        nullable=True,
    )

    date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    total_area = Column(
        Float,
        default=0.0,
    )

    mapped_area = Column(
        Float,
        default=0.0,
    )

    vegetation = Column(
        Float,
        default=0.0,
    )

    agriculture = Column(
        Float,
        default=0.0,
    )

    water = Column(
        Float,
        default=0.0,
    )

    builtup = Column(
        Float,
        default=0.0,
    )

    barren = Column(
        Float,
        default=0.0,
    )

    confidence = Column(
        Float,
        default=0.0,
    )

    status = Column(
        String,
        default="Completed",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    latitude = Column(
        Float,
        nullable=False,
    )

    longitude = Column(
        Float,
        nullable=False,
    )

    radius = Column(
        Float,
        nullable=False,
    )

    vegetation = Column(
        Float,
        default=0.0,
    )

    water = Column(
        Float,
        default=0.0,
    )

    builtup = Column(
        Float,
        default=0.0,
    )

    barren = Column(
        Float,
        default=0.0,
    )

    suitability_score = Column(
        Float,
        default=0.0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
