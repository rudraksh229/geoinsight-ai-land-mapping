
from geopy.exc import (
    GeocoderServiceError,
    GeocoderTimedOut,
)
from geopy.geocoders import Nominatim


def reverse_geocode(
    latitude,
    longitude,
):
    """
    Convert latitude and longitude into
    a human-readable location using Nominatim.
    """

    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Latitude and longitude must be valid numbers."
        ) from exc

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    try:
        geolocator = Nominatim(
            user_agent="geoinsight-ai"
        )

        location = geolocator.reverse(
            (latitude, longitude),
            exactly_one=True,
            timeout=10,
        )

        if location is None:
            return {
                "message": "Location not found."
            }

        address = location.raw.get(
            "address",
            {},
        )

        return {
            "latitude": latitude,
            "longitude": longitude,

            "village": (
                address.get("village")
                or address.get("hamlet")
                or address.get("suburb")
            ),

            "city": (
                address.get("city")
                or address.get("town")
                or address.get("municipality")
            ),

            "district": (
                address.get("county")
                or address.get("district")
            ),

            "state": address.get(
                "state"
            ),

            "country": address.get(
                "country"
            ),

            "postcode": address.get(
                "postcode"
            ),
        }

    except GeocoderTimedOut as exc:
        raise RuntimeError(
            "Reverse geocoding service timed out."
        ) from exc

    except GeocoderServiceError as exc:
        raise RuntimeError(
            f"Reverse geocoding service error: {exc}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Reverse geocoding failed: {exc}"
        ) from exc
