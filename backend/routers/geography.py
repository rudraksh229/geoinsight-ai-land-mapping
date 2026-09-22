from copy import deepcopy
import json
from urllib.request import Request, urlopen

from fastapi import APIRouter


router = APIRouter(
    prefix="/geography",
    tags=["Geography"],
)


# ============================================================
# INDIA STATES + UNION TERRITORIES
# ============================================================

STATE_CODES = {
    "Andhra Pradesh": "AP",
    "Arunachal Pradesh": "AR",
    "Assam": "AS",
    "Bihar": "BR",
    "Chhattisgarh": "CG",
    "Goa": "GA",
    "Gujarat": "GJ",
    "Haryana": "HR",
    "Himachal Pradesh": "HP",
    "Jharkhand": "JH",
    "Karnataka": "KA",
    "Kerala": "KL",
    "Madhya Pradesh": "MP",
    "Maharashtra": "MH",
    "Manipur": "MN",
    "Meghalaya": "ML",
    "Mizoram": "MZ",
    "Nagaland": "NL",
    "Odisha": "OD",
    "Punjab": "PB",
    "Rajasthan": "RJ",
    "Sikkim": "SK",
    "Tamil Nadu": "TN",
    "Telangana": "TS",
    "Tripura": "TR",
    "Uttar Pradesh": "UP",
    "Uttarakhand": "UK",
    "West Bengal": "WB",

    # Union Territories
    "Andaman and Nicobar Islands": "AN",
    "Chandigarh": "CH",
    "Dadra and Nagar Haveli and Daman and Diu": "DN",
    "Delhi": "DL",
    "Jammu and Kashmir": "JK",
    "Ladakh": "LA",
    "Lakshadweep": "LD",
    "Puducherry": "PY",
}


STATES = [
    {"code": code, "name": name}
    for name, code in STATE_CODES.items()
]


# ============================================================
# CURRENT INDIA DISTRICT DATA
# ============================================================
#
# The district directory below is fetched from a maintained
# dataset generated from the Government of India's IGOD
# State/UT district directory.
#
# This keeps the project from having a huge 700+ district
# hardcoded block inside this router.
#
# If the external source is temporarily unavailable, the
# application falls back to the legacy districts defined below.
#

DISTRICT_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "KTBsomen/Indian-state-district-json/"
    "main/india-states-districts-latest.json"
)


def normalize_code(value):
    """
    Convert a district name into a frontend-safe code.

    Example:
        'Madhya Pradesh' -> 'MADHYA_PRADESH'
        'Mumbai Suburban' -> 'MUMBAI_SUBURBAN'
    """
    code = value.upper()

    for char in [
        " ",
        "-",
        "/",
        ".",
        ",",
        "(",
        ")",
        "'",
        "&",
    ]:
        code = code.replace(char, "_")

    while "__" in code:
        code = code.replace("__", "_")

    return code.strip("_")


def build_districts_from_remote_data():
    """
    Fetch current State/UT -> District data.

    Returns:
        {
            "MP": [
                {"code": "INDORE", "name": "Indore"},
                ...
            ],
            ...
        }

    Returns empty dictionary if the remote source is unavailable.
    """

    try:
        request = Request(
            DISTRICT_DATA_URL,
            headers={
                "User-Agent": "GeoInsight-AI/1.0"
            },
        )

        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        result = {}

        for state_entry in data:
            state_name = state_entry.get("state")
            districts = state_entry.get("districts", [])

            state_code = STATE_CODES.get(state_name)

            if not state_code:
                continue

            result[state_code] = []

            for district_name in districts:
                district_name = str(district_name).strip()

                if not district_name:
                    continue

                result[state_code].append(
                    {
                        "code": normalize_code(district_name),
                        "name": district_name,
                    }
                )

        return result

    except Exception as error:
        print(
            f"[Geography] Could not load current district data: {error}"
        )
        return {}


# ============================================================
# LEGACY DISTRICT DATA
# ============================================================
#
# These are kept as a fallback so your old workflow continues
# working even if the external district source is unavailable.
#

LEGACY_DISTRICTS = {
    "MH": [
        {"code": "PUNE", "name": "Pune"},
        {"code": "MUMBAI", "name": "Mumbai"},
        {"code": "NAGPUR", "name": "Nagpur"},
    ],

    "MP": [
        {"code": "IND", "name": "Indore"},
        {"code": "BPL", "name": "Bhopal"},
    ],

    "RJ": [
        {"code": "JPR", "name": "Jaipur"},
        {"code": "JOD", "name": "Jodhpur"},
    ],

    "GJ": [
        {"code": "AMD", "name": "Ahmedabad"},
        {"code": "SRT", "name": "Surat"},
    ],

    "UP": [
        {"code": "GZB", "name": "Ghaziabad"},
        {"code": "LKO", "name": "Lucknow"},
        {"code": "AGRA", "name": "Agra"},
    ],
}


# ============================================================
# EXISTING VILLAGE / LOCATION DATA
# ============================================================
#
# IMPORTANT:
# These existing coordinates are preserved.
#
# They are representative analysis locations, not a complete
# village database for every district in India.
#

VILLAGES = {

    # --------------------------------------------------------
    # MAHARASHTRA
    # --------------------------------------------------------

    "PUNE": [
        {
            "code": "KHADAKWASLA",
            "name": "Khadakwasla",
            "lat": 18.4429,
            "lng": 73.7750,
        },
        {
            "code": "HINJEWADI",
            "name": "Hinjewadi",
            "lat": 18.5913,
            "lng": 73.7386,
        },
    ],

    "MUMBAI": [
        {
            "code": "BORIVALI",
            "name": "Borivali",
            "lat": 19.2307,
            "lng": 72.8567,
        },
    ],

    "NAGPUR": [
        {
            "code": "KORADI",
            "name": "Koradi",
            "lat": 21.2470,
            "lng": 79.0980,
        },
    ],


    # --------------------------------------------------------
    # MADHYA PRADESH
    # --------------------------------------------------------

    "IND": [
        {
            "code": "MHOW",
            "name": "Mhow",
            "lat": 22.5570,
            "lng": 75.7580,
        },
    ],

    "BPL": [
        {
            "code": "SEHORE",
            "name": "Sehore",
            "lat": 23.2032,
            "lng": 77.0844,
        },
    ],


    # --------------------------------------------------------
    # RAJASTHAN
    # --------------------------------------------------------

    "JPR": [
        {
            "code": "AMER",
            "name": "Amer",
            "lat": 26.9855,
            "lng": 75.8513,
        },
    ],

    "JOD": [
        {
            "code": "MANDORE",
            "name": "Mandore",
            "lat": 26.3547,
            "lng": 73.0487,
        },
    ],


    # --------------------------------------------------------
    # GUJARAT
    # --------------------------------------------------------

    "AMD": [
        {
            "code": "SANAND",
            "name": "Sanand",
            "lat": 22.9923,
            "lng": 72.3810,
        },
    ],

    "SRT": [
        {
            "code": "KAMREJ",
            "name": "Kamrej",
            "lat": 21.2737,
            "lng": 72.9577,
        },
    ],


    # --------------------------------------------------------
    # UTTAR PRADESH
    # --------------------------------------------------------

    "GZB": [
        {
            "code": "GHAZIABAD",
            "name": "Ghaziabad",
            "lat": 28.6692,
            "lng": 77.4538,
        },
    ],

    "LKO": [
        {
            "code": "LUCKNOW",
            "name": "Lucknow",
            "lat": 26.8467,
            "lng": 80.9462,
        },
    ],

    "AGRA": [
        {
            "code": "AGRA",
            "name": "Agra",
            "lat": 27.1767,
            "lng": 78.0081,
        },
    ],
}


# ============================================================
# BUILD FINAL DISTRICT DATA
# ============================================================

def build_final_district_data():
    """
    Build district data while preserving old district codes.

    New/current district names come from the current dataset.

    Existing codes such as:
        PUNE
        MUMBAI
        NAGPUR
        IND
        BPL
        JPR
        JOD
        AMD
        SRT
        GZB
        LKO
        AGRA

    are preserved so existing villages continue working.
    """

    remote_data = build_districts_from_remote_data()

    final_data = deepcopy(remote_data)

    for state_code, legacy_list in LEGACY_DISTRICTS.items():

        if state_code not in final_data:
            final_data[state_code] = []

        existing_names = {
            item["name"].strip().lower()
            for item in final_data[state_code]
        }

        for district in legacy_list:

            # If the district already exists by name,
            # replace its generated code with the old code.
            found = False

            for existing in final_data[state_code]:

                if (
                    existing["name"].strip().lower()
                    == district["name"].strip().lower()
                ):
                    existing["code"] = district["code"]
                    found = True
                    break

            # Otherwise append it.
            if not found:
                final_data[state_code].append(
                    deepcopy(district)
                )

    # If remote data failed completely, use legacy data.
    if not final_data:
        final_data = deepcopy(LEGACY_DISTRICTS)

    return final_data


DISTRICTS = build_final_district_data()


# ============================================================
# FINAL GEOGRAPHY OBJECT
# ============================================================

GEOGRAPHY_DATA = {
    "states": STATES,
    "districts": DISTRICTS,
    "villages": VILLAGES,
}


# ============================================================
# API ENDPOINT
# ============================================================

@router.get("/metadata")
def metadata():
    """
    Return geography metadata for the frontend.

    Existing frontend workflow remains unchanged:

        /geography/metadata
            ↓
        states
            ↓
        districts[state]
            ↓
        villages[district]
    """

    return deepcopy(GEOGRAPHY_DATA)