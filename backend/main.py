import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine
from models import Base

# Database sync guard
try:
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"Database sync warning: {db_err}")

# Safe Router Imports
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

# Explicit CORS Origins list for higher stability than regex
origins = [
    "https://geoinsight-ai-land-mapping.vercel.app",
    "https://geoinsight-ai-land-mapping-git-main-rudraksh229s-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Crash Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled Server Error: {str(exc)}")
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

# Router Registrations
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(geography.router)
app.include_router(landcover.router)
app.include_router(vegetation.router)
app.include_router(barren.router)
app.include_router(water.router)
app.include_router(builtup.router)
app.include_router(change.router)
app.include_router(suitability.router)
app.include_router(timeseries.router)
app.include_router(map.router)
app.include_router(geocode.router)
app.include_router(pdf.router)
app.include_router(recommendation.router)
app.include_router(satellite.router)
app.include_router(compare.router)
app.include_router(analytics.router)
app.include_router(csv_export.router)
app.include_router(excel_export.router)
app.include_router(auth.router)
app.include_router(polygon.router)
app.include_router(ai.router)
app.include_router(mapping.router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
