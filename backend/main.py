from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base

from routers import dashboard, reports
from routers import geography
from routers import landcover
from routers import vegetation
from routers import barren
from routers import water
from routers import builtup
from routers import change
from routers import suitability
from routers import timeseries
from routers import map
from routers import geocode
#from routers import report_generation
from routers import pdf
from routers import recommendation
from routers import satellite
from routers import compare
from routers import analytics
from routers import csv_export
from routers import excel_export
from routers import auth
from routers import polygon
from routers import ai
from routers import mapping
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
#app.include_router(report_generation.router)
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
