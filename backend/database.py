import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Render se environment variable uthayega, agar nahi mila toh local fallback use karega
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:GeoInsight%40123@localhost:5432/geoinsight_ai"
)

# Render URL "postgres://" return karta hai, par SQLAlchemy 2.0+ ko "postgresql://" chahiye
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        