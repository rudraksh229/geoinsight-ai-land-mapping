
import os

import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# ============================================================
# DATABASE
# ============================================================

from database import engine, Base
from models import User, Analysis, Report


# ============================================================
# ROUTERS
# ============================================================

try:
    from routers import (
        dashboard,
        reports,
        geography,
        landcover,
        vegetation,
        barren,
        water,
        builtup,
        change,
        suitability,
        timeseries,
        map,
        geocode,
        pdf,
        recommendation,
        satellite,
        compare,
        analytics,
        csv_export,
        excel_export,
        auth,
        polygon,
        ai,
        mapping,
    )

except ModuleNotFoundError:
    from backend.routers import (
        dashboard,
        reports,
        geography,
        landcover,
        vegetation,
        barren,
        water,
        builtup,
        change,
        suitability,
        timeseries,
        map,
        geocode,
        pdf,
        recommendation,
        satellite,
        compare,
        analytics,
        csv_export,
        excel_export,
        auth,
        polygon,
        ai,
        mapping,
    )


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="GeoInsight AI Engine",
    description="AI-based Land Mapping and Analysis API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

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
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH",
    ],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    """
    Initialize application resources when FastAPI starts.

    Database tables are created only if they do not already exist.
    Existing PostgreSQL data is not deleted or recreated.
    """

    print("=" * 60)
    print("GeoInsight AI backend starting...")
    print("=" * 60)

    try:
        Base.metadata.create_all(
            bind=engine
        )

        print(
            "[Database] PostgreSQL connection "
            "and table initialization successful."
        )

    except Exception as exc:
        print(
            "[Database] Initialization failed:"
        )
        print(
            str(exc)
        )

        # Do not silently hide a database failure.
        raise


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    print(
        f"[Unhandled Exception] "
        f"{request.method} {request.url}: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error.",
        },
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Land Mapping API Running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GeoInsight AI Engine",
    }


# ============================================================
# ROUTER REGISTRATION
# ============================================================

routers_list = [
    dashboard,
    reports,
    geography,
    landcover,
    vegetation,
    barren,
    water,
    builtup,
    change,
    suitability,
    timeseries,
    map,
    geocode,
    pdf,
    recommendation,
    satellite,
    compare,
    analytics,
    csv_export,
    excel_export,
    auth,
    polygon,
    ai,
    mapping,
]


for router_module in routers_list:
    app.include_router(
        router_module.router
    )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            8000,
        )
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
