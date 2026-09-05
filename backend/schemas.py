from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# ANALYSIS / REPORT SCHEMAS
# ============================================================

class AnalysisBase(BaseModel):
    village: str
    district: str
    state: str
    date: date

    total_area: float = 0.0
    mapped_area: float = 0.0

    vegetation: float = 0.0
    agriculture: float = 0.0
    water: float = 0.0
    builtup: float = 0.0
    barren: float = 0.0

    confidence: float = 0.0
    status: str = "Completed"


class AnalysisCreate(AnalysisBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None


class Analysis(AnalysisBase):
    id: int

    user_id: Optional[int] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# LAND MAPPING
# ============================================================

class AnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


class MappingRequest(BaseModel):
    state: str
    district: str
    village: str
    date: str
    lat: float
    lng: float
    radius: Optional[float] = 500


# ============================================================
# REPORT
# ============================================================

class SaveReportRequest(BaseModel):
    village: str
    district: str
    state: str

    latitude: float
    longitude: float
    radius: int


class ReportCreate(BaseModel):
    latitude: float
    longitude: float
    radius: float

    vegetation: float = 0.0
    water: float = 0.0
    builtup: float = 0.0
    barren: float = 0.0

    suitability_score: float = 0.0


class ReportResponse(ReportCreate):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# CHANGE DETECTION
# ============================================================

class ChangeRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int
    start_date: str
    end_date: str


# ============================================================
# SUITABILITY
# ============================================================

class SuitabilityRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


# ============================================================
# TIME SERIES
# ============================================================

class TimeSeriesRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int
    start_date: date
    end_date: date


# ============================================================
# VEGETATION
# ============================================================

class VegetationRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float

    start_date: date
    end_date: date


# ============================================================
# WATER
# ============================================================

class WaterRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


# ============================================================
# BUILT-UP
# ============================================================

class BuiltupRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


# ============================================================
# BARREN LAND
# ============================================================

class BarrenRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


# ============================================================
# LAND COVER
# ============================================================

class LandCoverRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


# ============================================================
# MAP
# ============================================================

class MapTileRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


# ============================================================
# GEOCODING
# ============================================================

class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float


# ============================================================
# COMPARE
# ============================================================

class Location(BaseModel):
    latitude: float
    longitude: float
    radius: float


class CompareRequest(BaseModel):
    location1: Location
    location2: Location


# ============================================================
# SATELLITE
# ============================================================

class SatelliteRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


# ============================================================
# PDF REPORT
# ============================================================

class PDFRequest(BaseModel):
    village: str
    district: str
    state: str
    date: str

    latitude: float
    longitude: float

    total_area: float

    vegetation: float
    water: float
    builtup: float
    barren: float

    ndvi: float
    ndwi: float
    ndbi: float

    prediction: str
    confidence: float

    recommendation: str


# ============================================================
# RECOMMENDATION
# ============================================================

class RecommendationRequest(BaseModel):
    vegetation_percent: float
    water_percent: float
    builtup_percent: float
    barren_percent: float
    average_ndvi: float


class RecommendationResponse(BaseModel):
    land_type: str
    recommendation: str
    priority: str
    confidence: float


# ============================================================
# AUTHENTICATION
# ============================================================

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
