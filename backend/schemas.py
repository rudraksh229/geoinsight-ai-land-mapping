from pydantic import BaseModel,EmailStr
from datetime import date

# --------------------------
# Database Schemas
# --------------------------

class AnalysisBase(BaseModel):
    village: str
    district: str
    state: str

    date: date

    total_area: float
    mapped_area: float

    confidence: float

    status: str


class AnalysisCreate(AnalysisBase):
    pass


class Analysis(AnalysisBase):
    id: int

    class Config:
        from_attributes = True


# --------------------------
# Earth Engine Request Schema
# --------------------------

class AnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


# --------------------------
# Save Report Schema
# --------------------------

class SaveReportRequest(BaseModel):
    village: str
    district: str
    state: str

    latitude: float
    longitude: float
    radius: int
class ChangeRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int
    start_date: str
    end_date: str
class SuitabilityRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int
class TimeSeriesRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int

    start_date: date
    end_date: date
class MapTileRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int
class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float
class ReportCreate(BaseModel):
    latitude: float
    longitude: float
    radius: float

    vegetation: float
    water: float
    builtup: float
    barren: float

    suitability_score: float


class ReportResponse(ReportCreate):
    id: int

    class Config:
        from_attributes = True
class PDFRequest(BaseModel):
    # Location Details
    village: str
    district: str
    state: str

    # Analysis Information
    date: str

    latitude: float
    longitude: float

    total_area: float

    vegetation: float
    water: float
    builtup: float
    barren: float

    # Satellite Statistics
    ndvi: float
    ndwi: float
    ndbi: float

    # AI Prediction
    prediction: str
    confidence: float

    # AI Recommendation
    recommendation: str
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
class SatelliteRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float
from pydantic import BaseModel
class MappingRequest(BaseModel):
    state: str
    district: str
    village: str
    date: str

    lat: float
    lng: float

class Location(BaseModel):
    latitude: float
    longitude: float
    radius: float


class CompareRequest(BaseModel):
    location1: Location
    location2: Location
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
