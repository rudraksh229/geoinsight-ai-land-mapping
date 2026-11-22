from datetime import datetime
from typing import Optional, Dict, Any


class User:
    collection_name = "users"

    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        email: str = "",
        password_hash: str = "",
        role: str = "user",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["User"]:
        if not doc:
            return None
        return cls(**doc)


class Analysis:
    collection_name = "analysis"

    def __init__(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        village: Optional[str] = "Amer",
        district: Optional[str] = "JPR",
        state: Optional[str] = "RJ",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[float] = None,
        date: Optional[datetime] = None,
        total_area: float = 0.0,
        mapped_area: float = 0.0,
        vegetation: float = 0.0,
        agriculture: float = 0.0,
        water: float = 0.0,
        builtup: float = 0.0,
        barren: float = 0.0,
        confidence: float = 0.0,
        status: str = "Completed",
        created_at: Optional[datetime] = None,
        **kwargs,
    ):
        self.id = id
        self.user_id = user_id
        self.village = village
        self.district = district
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.date = date or datetime.utcnow()
        self.total_area = total_area
        self.mapped_area = mapped_area
        self.vegetation = vegetation
        self.agriculture = agriculture
        self.water = water
        self.builtup = builtup
        self.barren = barren
        self.confidence = confidence
        self.status = status
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "village": self.village,
            "district": self.district,
            "state": self.state,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "date": self.date,
            "total_area": self.total_area,
            "mapped_area": self.mapped_area,
            "vegetation": self.vegetation,
            "agriculture": self.agriculture,
            "water": self.water,
            "builtup": self.builtup,
            "barren": self.barren,
            "confidence": self.confidence,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Analysis"]:
        if not doc:
            return None
        return cls(**doc)


class Report:
    collection_name = "reports"

    def __init__(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        radius: float = 0.0,
        vegetation: float = 0.0,
        water: float = 0.0,
        builtup: float = 0.0,
        barren: float = 0.0,
        suitability_score: float = 0.0,
        created_at: Optional[datetime] = None,
        **kwargs,
    ):
        self.id = id
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.vegetation = vegetation
        self.water = water
        self.builtup = builtup
        self.barren = barren
        self.suitability_score = suitability_score
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "vegetation": self.vegetation,
            "water": self.water,
            "builtup": self.builtup,
            "barren": self.barren,
            "suitability_score": self.suitability_score,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Report"]:
        if not doc:
            return None
        return cls(**doc)
