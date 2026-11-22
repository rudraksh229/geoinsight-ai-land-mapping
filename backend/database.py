import os
import certifi
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("DATABASE_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "geoinsight_ai")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI environment variable is not set. "
        "Please configure your MongoDB connection string."
    )


# ============================================================
# MONGODB CLIENT & DATABASE
# ============================================================

client = MongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    maxPoolSize=10,
)

mongo_db = client[MONGO_DB_NAME]


# ============================================================
# AUTO-INCREMENT ID HELPER (Keeps PostgreSQL integer ID compatibility)
# ============================================================

def get_next_sequence(sequence_name: str) -> int:
    """
    Generate sequential integer IDs (1, 2, 3...) in MongoDB
    so existing frontend routes and integer ID checks continue working.
    """
    counter = mongo_db["counters"].find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(counter["seq"])


# ============================================================
# STARTUP INDEX INITIALIZATION
# ============================================================

def init_db():
    """
    Verify MongoDB connection and create required indexes.
    """
    client.admin.command("ping")

    mongo_db["users"].create_index("id", unique=True)
    mongo_db["users"].create_index("email", unique=True)

    mongo_db["analysis"].create_index("id", unique=True)
    mongo_db["analysis"].create_index("user_id")

    mongo_db["reports"].create_index("id", unique=True)
    mongo_db["reports"].create_index("user_id")


# ============================================================
# FASTAPI DATABASE DEPENDENCY
# ============================================================

def get_db():
    """
    Yield the MongoDB database instance so existing
    Depends(get_db) signatures in routers require zero changes.
    """
    try:
        yield mongo_db
    except PyMongoError as exc:
        print(f"[Database Error] {exc}")
        raise
    