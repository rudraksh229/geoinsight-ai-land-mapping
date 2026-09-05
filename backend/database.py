import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Environment variable check with fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:GeoInsight%40123@localhost:5432/geoinsight_ai"
)

# Render Postgres Dialect Compatibility Guard
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Memory & Connection Pool Management for Render Free Tier (512MB RAM Limit)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Automatically reconnects dead/stale connections
    pool_recycle=300,        # Recycles connections every 5 minutes to prevent idle drops
    pool_size=5,             # Restricts max persistent connections
    max_overflow=10,         # Allows burst queries up to 10 extra temporary connections
    connect_args={"connect_timeout": 10} # Prevents hanging requests during database outages
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# FastAPI Dependency for Clean Context Management
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as db_err:
        db.rollback()
        print(f"[Database Session Error]: {str(db_err)}")
        raise
    finally:
        db.close()
