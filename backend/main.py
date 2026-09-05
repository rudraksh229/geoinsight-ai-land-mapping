import json
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 1. EARTH ENGINE & SERVICE KEY GUARD (Execution safe initialization)
try:
    ee_key_str = os.getenv("EE_SERVICE_ACCOUNT_KEY")
    if ee_key_str:
        # Check if JSON format needs parsing verification
        if isinstance(ee_key_str, str) and ee_key_str.strip().startswith("{"):
            pass  # Key present in correct JSON format
except Exception as ee_err:
    print(f"[Warning] Earth Engine Key Pre-check Warning: {ee_err}")

# 2. DATABASE SYNC GUARD
try:
    from database import engine
    from models import Base
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"[Warning] Database auto-creation skipped/failed: {db_err}")

# 3. ROUTER IMPORTS GUARD
try:
    from routers import (
        dashboard, reports, geography, landcover, vegetation, 
        barren, water, builtup, change, suitability, timeseries, 
        map, geocode, pdf, recommendation, satellite, compare, 
        analytics, csv_export, excel_export, auth, polygon, ai, mapping
    )
except ModuleNotFoundError:
    from backend.routers import (
        dashboard, reports, geography, landcover, vegetation, 
        barren, water, builtup, change, suitability, timeseries, 
        map, geocode, pdf, recommendation, satellite, compare, 
        analytics, csv_export, excel_export, auth, polygon, ai, mapping
    )

app = FastAPI(title="GeoInsight AI Engine")

# 4. ROBUST PRODUCTION CORS SETUP
origins = [
    "https://geoinsight-ai-land-mapping.vercel.app",
    "https://geoinsight-ai-land-mapping-git-main-rudraksh229s-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 5. GLOBAL EXCEPTION HANDLER FOR UNCAUGHT API ERRORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[Unhandled Exception]: {str(exc)}")
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Server Error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": origin if origin else "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        }
    )

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Land Mapping API Running"}

# 6. ROUTER REGISTRATIONS
routers_list = [
    dashboard, reports, geography, landcover, vegetation, 
    barren, water, builtup, change, suitability, timeseries, 
    map, geocode, pdf, recommendation, satellite, compare, 
    analytics, csv_export, excel_export, auth, polygon, ai, mapping
]

for r in routers_list:
    app.include_router(r.router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
