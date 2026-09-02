from geopy.geocoders import Nominatim


def reverse_geocode(latitude, longitude):

    geolocator = Nominatim(user_agent="geoinsight-ai")

    location = geolocator.reverse(
        (latitude, longitude),
        exactly_one=True
    )

    if location is None:
        return {
            "message": "Location not found."
        }

    address = location.raw.get("address", {})

    return {
        "latitude": latitude,
        "longitude": longitude,
        "village": address.get("village")
            or address.get("hamlet")
            or address.get("suburb"),

        "city": address.get("city")
            or address.get("town"),

        "district": address.get("county"),

        "state": address.get("state"),

        "country": address.get("country"),

        "postcode": address.get("postcode")
    }
