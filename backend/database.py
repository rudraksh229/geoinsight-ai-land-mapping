
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please configure the Render PostgreSQL DATABASE_URL."
    )


# Render may provide the old postgres:// format.
# SQLAlchemy expects postgresql://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1,
    )


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,

    # Detect stale/dead connections before using them.
    pool_pre_ping=True,

    # Recycle connections periodically.
    pool_recycle=300,

    # Keep the connection pool small for Render.
    pool_size=3,

    # Allow a small number of temporary connections
    # during short traffic bursts.
    max_overflow=2,

    # Prevent requests from hanging indefinitely
    # when PostgreSQL is unreachable.
    connect_args={
        "connect_timeout": 10,
    },
)


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# FASTAPI DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    except Exception as exc:
        db.rollback()

        print(
            f"[Database Session Error] {exc}"
        )

        raise

    finally:
        db.close()
