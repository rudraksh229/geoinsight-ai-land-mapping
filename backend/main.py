import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine
from models import Base

# Database tables setup inside try-except to avoid boot crash
try:
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"Database sync warning: {db_err}")

from routers import (
    dashboard, reports, geography, landcover, vegetation, 
    barren, water, builtup, change, suitability, timeseries, 
    map, geocode, pdf, recommendation, satellite, compare, 
    analytics, csv_export, excel_export, auth, polygon, ai, mapping
)

app = FastAPI()

# Perfect CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",  # Sabhi Vercel aur Localhost domains allow karega
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Crash Handler: 502/Crash ki jagah clean CORS-friendly JSON Error response dega
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled Server Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Server Error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Land Mapping API Running"}

# Include Routers
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
    