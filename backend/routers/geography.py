from copy import deepcopy
import json
from urllib.request import Request, urlopen

from fastapi import APIRouter

router = APIRouter(prefix="/geography", tags=["Geography"])


# ============================================================
# STATES
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
    {
        "code": code,
        "name": name,
    }
    for name, code in STATE_CODES.items()
]


# ============================================================
# DISTRICT DATA
#
# Only district names are loaded.
# NO village dataset is downloaded.
# ============================================================

DISTRICT_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "KTBsomen/Indian-state-district-json/"
    "main/india-states-districts-latest.json"
)


def normalize_code(value):
    """
    Convert a name into a frontend-safe code.

    Example:
        Madhya Pradesh -> MADHYA_PRADESH
        Mumbai Suburban -> MUMBAI_SUBURBAN
    """

    code = str(value).upper()

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
    Loads district names only.

    This does NOT load villages.
    """

    try:
        request = Request(
            DISTRICT_DATA_URL,
            headers={
                "User-Agent": "GeoInsight-AI/1.0"
            },
        )

        with urlopen(request, timeout=10) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        result = {}

        for state_entry in data:

            state_name = state_entry.get("state")

            districts = state_entry.get(
                "districts",
                [],
            )

            state_code = STATE_CODES.get(
                state_name
            )

            if not state_code:
                continue

            result[state_code] = []

            for district_name in districts:

                district_name = str(
                    district_name
                ).strip()

                if not district_name:
                    continue

                result[state_code].append(
                    {
                        "code": normalize_code(
                            district_name
                        ),
                        "name": district_name,
                    }
                )

        return result

    except Exception as error:

        print(
            f"[Geography] Could not load "
            f"district data: {error}"
        )

        return {}


# ============================================================
# LEGACY DISTRICTS
#
# These codes MUST remain unchanged because the existing
# frontend/backend may already depend on them.
# ============================================================

LEGACY_DISTRICTS = {

    "MH": [
        {
            "code": "PUNE",
            "name": "Pune",
        },
        {
            "code": "MUMBAI",
            "name": "Mumbai",
        },
        {
            "code": "NAGPUR",
            "name": "Nagpur",
        },
    ],

    "MP": [
        {
            "code": "IND",
            "name": "Indore",
        },
        {
            "code": "BPL",
            "name": "Bhopal",
        },
    ],

    "RJ": [
        {
            "code": "JPR",
            "name": "Jaipur",
        },
        {
            "code": "JOD",
            "name": "Jodhpur",
        },
    ],

    "GJ": [
        {
            "code": "AMD",
            "name": "Ahmedabad",
        },
        {
            "code": "SRT",
            "name": "Surat",
        },
    ],

    "UP": [
        {
            "code": "GZB",
            "name": "Ghaziabad",
        },
        {
            "code": "LKO",
            "name": "Lucknow",
        },
        {
            "code": "AGRA",
            "name": "Agra",
        },
    ],
}


# ============================================================
# EXISTING VILLAGES
#
# DO NOT REMOVE.
# ============================================================

VILLAGES = {

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
# KNOWN DISTRICT HQ COORDINATES
#
# These are static.
# Nothing is downloaded at runtime.
#
# Format:
# NORMALIZED_DISTRICT_NAME:
# {
#     "lat": latitude,
#     "lng": longitude
# }
# ============================================================

DISTRICT_HQ_COORDINATES = {

    # --------------------------------------------------------
    # MADHYA PRADESH
    # --------------------------------------------------------

    "BHOPAL": {
        "lat": 23.2599,
        "lng": 77.4126,
    },

    "INDORE": {
        "lat": 22.7196,
        "lng": 75.8577,
    },

    "UJJAIN": {
        "lat": 23.1765,
        "lng": 75.7885,
    },

    "DEWAS": {
        "lat": 22.9676,
        "lng": 76.0534,
    },

    "SEHORE": {
        "lat": 23.2032,
        "lng": 77.0844,
    },

    "VIDISHA": {
        "lat": 23.5251,
        "lng": 77.8081,
    },

    "RAISEN": {
        "lat": 23.3315,
        "lng": 77.7812,
    },

    "NARMADAPURAM": {
        "lat": 22.7441,
        "lng": 77.7360,
    },

    "HOSHANGABAD": {
        "lat": 22.7441,
        "lng": 77.7360,
    },

    "MANDSAUR": {
        "lat": 24.0718,
        "lng": 75.0697,
    },

    "RATLAM": {
        "lat": 23.3315,
        "lng": 75.0367,
    },

    "SAGAR": {
        "lat": 23.8388,
        "lng": 78.7378,
    },

    "REWA": {
        "lat": 24.5362,
        "lng": 81.3037,
    },

    "SATNA": {
        "lat": 24.6005,
        "lng": 80.8322,
    },

    "JABALPUR": {
        "lat": 23.1815,
        "lng": 79.9864,
    },

    "GWALIOR": {
        "lat": 26.2183,
        "lng": 78.1828,
    },

    "MORENA": {
        "lat": 26.4947,
        "lng": 77.9940,
    },

    "BHIND": {
        "lat": 26.5640,
        "lng": 78.7886,
    },

    "SHIVPURI": {
        "lat": 25.4238,
        "lng": 77.7390,
    },

    "GUNA": {
        "lat": 24.6469,
        "lng": 77.3113,
    },

    "CHHINDWARA": {
        "lat": 22.0574,
        "lng": 78.9382,
    },

    "BETUL": {
        "lat": 21.9108,
        "lng": 77.9026,
    },

    "KHANDWA": {
        "lat": 21.8247,
        "lng": 76.3526,
    },

    "KHARGONE": {
        "lat": 21.8234,
        "lng": 75.6137,
    },

    "BARWANI": {
        "lat": 22.0320,
        "lng": 74.9000,
    },

    "DHAR": {
        "lat": 22.6013,
        "lng": 75.3025,
    },

    "JHABUA": {
        "lat": 22.7695,
        "lng": 74.5921,
    },

    "ALIRAJPUR": {
        "lat": 22.3053,
        "lng": 74.3640,
    },

    "MANDLA": {
        "lat": 22.5986,
        "lng": 80.3714,
    },

    "BALAGHAT": {
        "lat": 21.8120,
        "lng": 80.1838,
    },

    "DINDORI": {
        "lat": 22.9417,
        "lng": 81.0790,
    },

    "ANUPPUR": {
        "lat": 23.1031,
        "lng": 81.6900,
    },

    "SHAHDOL": {
        "lat": 23.3017,
        "lng": 81.3560,
    },

    "SINGRAULI": {
        "lat": 24.1997,
        "lng": 82.6753,
    },

    "PANNA": {
        "lat": 24.7180,
        "lng": 80.1819,
    },

    "CHHATARPUR": {
        "lat": 24.9164,
        "lng": 79.5812,
    },

    "TIKAMGARH": {
        "lat": 24.7433,
        "lng": 78.8318,
    },

    "DATIA": {
        "lat": 25.6731,
        "lng": 78.4591,
    },

    "SHEOPUR": {
        "lat": 25.6700,
        "lng": 76.6961,
    },

    # --------------------------------------------------------
    # MAHARASHTRA
    # --------------------------------------------------------

    "PUNE": {
        "lat": 18.5204,
        "lng": 73.8567,
    },

    "MUMBAI": {
        "lat": 19.0760,
        "lng": 72.8777,
    },

    "NAGPUR": {
        "lat": 21.1458,
        "lng": 79.0882,
    },

    "NASHIK": {
        "lat": 20.0059,
        "lng": 73.7910,
    },

    "AHMEDNAGAR": {
        "lat": 19.0948,
        "lng": 74.7480,
    },

    "AURANGABAD": {
        "lat": 19.8762,
        "lng": 75.3433,
    },

    "CHHATRAPATI_SAMBHAJINAGAR": {
        "lat": 19.8762,
        "lng": 75.3433,
    },

    "KOLHAPUR": {
        "lat": 16.7050,
        "lng": 74.2433,
    },

    "SOLAPUR": {
        "lat": 17.6599,
        "lng": 75.9064,
    },

    "SATARA": {
        "lat": 17.6805,
        "lng": 74.0183,
    },

    "SANGLI": {
        "lat": 16.8524,
        "lng": 74.5815,
    },

    "JALGAON": {
        "lat": 21.0077,
        "lng": 75.5626,
    },

    "AMRAVATI": {
        "lat": 20.9374,
        "lng": 77.7796,
    },

    "AKOLA": {
        "lat": 20.7002,
        "lng": 77.0082,
    },

    "NANDED": {
        "lat": 19.1383,
        "lng": 77.3210,
    },

    "LATUR": {
        "lat": 18.4088,
        "lng": 76.5604,
    },

    "BEED": {
        "lat": 18.9891,
        "lng": 75.7601,
    },

    "PARBHANI": {
        "lat": 19.2608,
        "lng": 76.7750,
    },

    "OSMANABAD": {
        "lat": 18.1860,
        "lng": 76.0419,
    },

    "DHULE": {
        "lat": 20.9042,
        "lng": 74.7749,
    },

    "NANDURBAR": {
        "lat": 21.3667,
        "lng": 74.2333,
    },

    "WARDHA": {
        "lat": 20.7453,
        "lng": 78.6022,
    },

    "YAVATMAL": {
        "lat": 20.3888,
        "lng": 78.1204,
    },

    "BULDHANA": {
        "lat": 20.5293,
        "lng": 76.1842,
    },

    "GADCHIROLI": {
        "lat": 20.1809,
        "lng": 80.0030,
    },

    "CHANDRAPUR": {
        "lat": 19.9705,
        "lng": 79.3034,
    },

    "GONDIA": {
        "lat": 21.4624,
        "lng": 80.2210,
    },

    "RATNAGIRI": {
        "lat": 16.9902,
        "lng": 73.3120,
    },

    "SINDHUDURG": {
        "lat": 16.3492,
        "lng": 73.5594,
    },

    # --------------------------------------------------------
    # GUJARAT
    # --------------------------------------------------------

    "AHMEDABAD": {
        "lat": 23.0225,
        "lng": 72.5714,
    },

    "SURAT": {
        "lat": 21.1702,
        "lng": 72.8311,
    },

    "VADODARA": {
        "lat": 22.3072,
        "lng": 73.1812,
    },

    "RAJKOT": {
        "lat": 22.3039,
        "lng": 70.8022,
    },

    "BHAVNAGAR": {
        "lat": 21.7645,
        "lng": 72.1519,
    },

    "JAMNAGAR": {
        "lat": 22.4707,
        "lng": 70.0577,
    },

    "JUNAGADH": {
        "lat": 21.5222,
        "lng": 70.4579,
    },

    "GANDHINAGAR": {
        "lat": 23.2156,
        "lng": 72.6369,
    },

    "ANAND": {
        "lat": 22.5645,
        "lng": 72.9289,
    },

    "BHARUCH": {
        "lat": 21.7051,
        "lng": 72.9959,
    },

    "VALSAD": {
        "lat": 20.5992,
        "lng": 72.9342,
    },

    "NAVSARI": {
        "lat": 20.9467,
        "lng": 72.9520,
    },

    "MEHSANA": {
        "lat": 23.5880,
        "lng": 72.3693,
    },

    "PATAN": {
        "lat": 23.8493,
        "lng": 72.1266,
    },

    "MORBI": {
        "lat": 22.8110,
        "lng": 70.8236,
    },

    "PORBANDAR": {
        "lat": 21.6417,
        "lng": 69.6293,
    },

    # --------------------------------------------------------
    # RAJASTHAN
    # --------------------------------------------------------

    "JAIPUR": {
        "lat": 26.9124,
        "lng": 75.7873,
    },

    "JODHPUR": {
        "lat": 26.2389,
        "lng": 73.0243,
    },

    "AJMER": {
        "lat": 26.4499,
        "lng": 74.6399,
    },

    "KOTA": {
        "lat": 25.2138,
        "lng": 75.8648,
    },

    "UDAIPUR": {
        "lat": 24.5854,
        "lng": 73.7125,
    },

    "BIKANER": {
        "lat": 28.0229,
        "lng": 73.3119,
    },

    "ALWAR": {
        "lat": 27.5530,
        "lng": 76.6346,
    },

    "BHARATPUR": {
        "lat": 27.2152,
        "lng": 77.4903,
    },

    "SIKAR": {
        "lat": 27.6094,
        "lng": 75.1399,
    },

    "PALI": {
        "lat": 25.7711,
        "lng": 73.3234,
    },

    "NAGAUR": {
        "lat": 27.2020,
        "lng": 73.7400,
    },

    "BARMER": {
        "lat": 25.7521,
        "lng": 71.3967,
    },

    "JHALAWAR": {
        "lat": 24.5973,
        "lng": 76.1603,
    },

    # --------------------------------------------------------
    # UTTAR PRADESH
    # --------------------------------------------------------

    "LUCKNOW": {
        "lat": 26.8467,
        "lng": 80.9462,
    },

    "AGRA": {
        "lat": 27.1767,
        "lng": 78.0081,
    },

    "KANPUR_NAGAR": {
        "lat": 26.4499,
        "lng": 80.3319,
    },

    "VARANASI": {
        "lat": 25.3176,
        "lng": 82.9739,
    },

    "PRAYAGRAJ": {
        "lat": 25.4358,
        "lng": 81.8463,
    },

    "ALLAHABAD": {
        "lat": 25.4358,
        "lng": 81.8463,
    },

    "MEERUT": {
        "lat": 28.9845,
        "lng": 77.7064,
    },

    "GHAZIABAD": {
        "lat": 28.6692,
        "lng": 77.4538,
    },

    "NOIDA": {
        "lat": 28.5355,
        "lng": 77.3910,
    },

    "GORAKHPUR": {
        "lat": 26.7606,
        "lng": 83.3732,
    },

    "BAREILLY": {
        "lat": 28.3670,
        "lng": 79.4304,
    },

    "MORADABAD": {
        "lat": 28.8386,
        "lng": 78.7733,
    },

    "AYODHYA": {
        "lat": 26.7990,
        "lng": 82.2047,
    },

    "MATHURA": {
        "lat": 27.4924,
        "lng": 77.6737,
    },

    "ALIGARH": {
        "lat": 27.8974,
        "lng": 78.0880,
    },

    "JHANSI": {
        "lat": 25.4484,
        "lng": 78.5685,
    },

    "MIRZAPUR": {
        "lat": 25.1337,
        "lng": 82.5644,
    },

    # --------------------------------------------------------
    # BIHAR
    # --------------------------------------------------------

    "PATNA": {
        "lat": 25.5941,
        "lng": 85.1376,
    },

    "GAYA": {
        "lat": 24.7914,
        "lng": 85.0002,
    },

    "MUZAFFARPUR": {
        "lat": 26.1197,
        "lng": 85.3910,
    },

    "BHAGALPUR": {
        "lat": 25.2425,
        "lng": 86.9842,
    },

    "DARBHANGA": {
        "lat": 26.1542,
        "lng": 85.8918,
    },

    "PURNIA": {
        "lat": 25.7771,
        "lng": 87.4753,
    },

    "ARA": {
        "lat": 25.5560,
        "lng": 84.6633,
    },

    "BHOJPUR": {
        "lat": 25.5560,
        "lng": 84.6633,
    },

    "BEGUSARAI": {
        "lat": 25.4182,
        "lng": 86.1272,
    },

    # --------------------------------------------------------
    # WEST BENGAL
    # --------------------------------------------------------

    "KOLKATA": {
        "lat": 22.5726,
        "lng": 88.3639,
    },

    "DARJEELING": {
        "lat": 27.0410,
        "lng": 88.2663,
    },

    "HOWRAH": {
        "lat": 22.5958,
        "lng": 88.2636,
    },

    "SILIGURI": {
        "lat": 26.7271,
        "lng": 88.3953,
    },

    "MALDA": {
        "lat": 25.0108,
        "lng": 88.1411,
    },

    "ASANSOL": {
        "lat": 23.6739,
        "lng": 87.0890,
    },

    "DURGAPUR": {
        "lat": 23.5204,
        "lng": 87.3119,
    },

    # --------------------------------------------------------
    # KARNATAKA
    # --------------------------------------------------------

    "BENGALURU_URBAN": {
        "lat": 12.9716,
        "lng": 77.5946,
    },

    "BANGALORE_URBAN": {
        "lat": 12.9716,
        "lng": 77.5946,
    },

    "MYSURU": {
        "lat": 12.2958,
        "lng": 76.6394,
    },

    "MANGALURU": {
        "lat": 12.9141,
        "lng": 74.8560,
    },

    "DAKSHINA_KANNADA": {
        "lat": 12.9141,
        "lng": 74.8560,
    },

    "HUBBALLI_DHARWAD": {
        "lat": 15.3647,
        "lng": 75.1240,
    },

    "BELAGAVI": {
        "lat": 15.8497,
        "lng": 74.4977,
    },

    "BALLARI": {
        "lat": 15.1394,
        "lng": 76.9214,
    },

    "SHIVAMOGGA": {
        "lat": 13.9299,
        "lng": 75.5681,
    },

    "TUMAKURU": {
        "lat": 13.3392,
        "lng": 77.1130,
    },

    "KALABURAGI": {
        "lat": 17.3297,
        "lng": 76.8343,
    },

    "KALABURAGI_GULBARGA": {
        "lat": 17.3297,
        "lng": 76.8343,
    },

    # --------------------------------------------------------
    # TAMIL NADU
    # --------------------------------------------------------

    "CHENNAI": {
        "lat": 13.0827,
        "lng": 80.2707,
    },

    "COIMBATORE": {
        "lat": 11.0168,
        "lng": 76.9558,
    },

    "MADURAI": {
        "lat": 9.9252,
        "lng": 78.1198,
    },

    "SALEM": {
        "lat": 11.6643,
        "lng": 78.1460,
    },

    "TIRUCHIRAPPALLI": {
        "lat": 10.7905,
        "lng": 78.7047,
    },

    "TRICHY": {
        "lat": 10.7905,
        "lng": 78.7047,
    },

    "TIRUNELVELI": {
        "lat": 8.7139,
        "lng": 77.7567,
    },

    "ERODE": {
        "lat": 11.3410,
        "lng": 77.7172,
    },

    "VELLORE": {
        "lat": 12.9165,
        "lng": 79.1325,
    },

    "THANJAVUR": {
        "lat": 10.7870,
        "lng": 79.1378,
    },

    # --------------------------------------------------------
    # TELANGANA
    # --------------------------------------------------------

    "HYDERABAD": {
        "lat": 17.3850,
        "lng": 78.4867,
    },

    "WARANGAL": {
        "lat": 17.9689,
        "lng": 79.5941,
    },

    "NIZAMABAD": {
        "lat": 18.6725,
        "lng": 78.0941,
    },

    "KARIMNAGAR": {
        "lat": 18.4386,
        "lng": 79.1288,
    },

    "KHAMMAM": {
        "lat": 17.2473,
        "lng": 80.1514,
    },

    "NALGONDA": {
        "lat": 17.0575,
        "lng": 79.2684,
    },

    # --------------------------------------------------------
    # ANDHRA PRADESH
    # --------------------------------------------------------

    "VISAKHAPATNAM": {
        "lat": 17.6868,
        "lng": 83.2185,
    },

    "VIJAYAWADA": {
        "lat": 16.5062,
        "lng": 80.6480,
    },

    "TIRUPATI": {
        "lat": 13.6288,
        "lng": 79.4192,
    },

    "GUNTUR": {
        "lat": 16.3067,
        "lng": 80.4365,
    },

    "KURNOOL": {
        "lat": 15.8281,
        "lng": 78.0373,
    },

    "NELLORE": {
        "lat": 14.4426,
        "lng": 79.9865,
    },

    "KAKINADA": {
        "lat": 16.9891,
        "lng": 82.2475,
    },

    # --------------------------------------------------------
    # ODISHA
    # --------------------------------------------------------

    "KHORDHA": {
        "lat": 20.2961,
        "lng": 85.8245,
    },

    "CUTTACK": {
        "lat": 20.4625,
        "lng": 85.8830,
    },

    "PURI": {
        "lat": 19.8135,
        "lng": 85.8312,
    },

    "SAMBALPUR": {
        "lat": 21.4669,
        "lng": 83.9812,
    },

    "BALASORE": {
        "lat": 21.4942,
        "lng": 86.9317,
    },

    "BERHAMPUR": {
        "lat": 19.3149,
        "lng": 84.7941,
    },

    # --------------------------------------------------------
    # KERALA
    # --------------------------------------------------------

    "THIRUVANANTHAPURAM": {
        "lat": 8.5241,
        "lng": 76.9366,
    },

    "ERNAKULAM": {
        "lat": 9.9312,
        "lng": 76.2673,
    },

    "KOCHI": {
        "lat": 9.9312,
        "lng": 76.2673,
    },

    "KOZHIKODE": {
        "lat": 11.2588,
        "lng": 75.7804,
    },

    "THRISSUR": {
        "lat": 10.5276,
        "lng": 76.2144,
    },

    "KOLLAM": {
        "lat": 8.8932,
        "lng": 76.6141,
    },

    "KANNUR": {
        "lat": 11.8745,
        "lng": 75.3704,
    },

    # --------------------------------------------------------
    # PUNJAB
    # --------------------------------------------------------

    "LUDHIANA": {
        "lat": 30.9010,
        "lng": 75.8573,
    },

    "AMRITSAR": {
        "lat": 31.6340,
        "lng": 74.8723,
    },

    "JALANDHAR": {
        "lat": 31.3260,
        "lng": 75.5762,
    },

    "PATIALA": {
        "lat": 30.3398,
        "lng": 76.3869,
    },

    "BATHINDA": {
        "lat": 30.2110,
        "lng": 74.9455,
    },

    "MOHALI": {
        "lat": 30.7046,
        "lng": 76.7179,
    },

    # --------------------------------------------------------
    # HARYANA
    # --------------------------------------------------------

    "GURUGRAM": {
        "lat": 28.4595,
        "lng": 77.0266,
    },

    "FARIDABAD": {
        "lat": 28.4089,
        "lng": 77.3178,
    },

    "PANIPAT": {
        "lat": 29.3909,
        "lng": 76.9635,
    },

    "ROHTAK": {
        "lat": 28.8955,
        "lng": 76.6066,
    },

    "HISAR": {
        "lat": 29.1492,
        "lng": 75.7217,
    },

    "KARNAL": {
        "lat": 29.6857,
        "lng": 76.9905,
    },

    # --------------------------------------------------------
    # JHARKHAND
    # --------------------------------------------------------

    "RANCHI": {
        "lat": 23.3441,
        "lng": 85.3096,
    },

    "DHANBAD": {
        "lat": 23.7957,
        "lng": 86.4304,
    },

    "JAMTARA": {
        "lat": 23.9631,
        "lng": 86.8024,
    },

    "JAMSHEDPUR": {
        "lat": 22.8046,
        "lng": 86.2029,
    },

    "EAST_SINGHBHUM": {
        "lat": 22.8046,
        "lng": 86.2029,
    },

    "BOKARO": {
        "lat": 23.6693,
        "lng": 86.1511,
    },

    "DEOGHAR": {
        "lat": 24.4922,
        "lng": 86.6944,
    },

    # --------------------------------------------------------
    # CHHATTISGARH
    # --------------------------------------------------------

    "RAIPUR": {
        "lat": 21.2514,
        "lng": 81.6296,
    },

    "BILASPUR": {
        "lat": 22.0797,
        "lng": 82.1409,
    },

    "DURG": {
        "lat": 21.1904,
        "lng": 81.2849,
    },

    "RAJNANDGAON": {
        "lat": 21.0972,
        "lng": 81.0288,
    },

    "KORBA": {
        "lat": 22.3595,
        "lng": 82.7501,
    },

    "JAGDALPUR": {
        "lat": 19.0748,
        "lng": 82.0080,
    },

    # --------------------------------------------------------
    # HIMACHAL PRADESH
    # --------------------------------------------------------

    "SHIMLA": {
        "lat": 31.1048,
        "lng": 77.1734,
    },

    "KANGRA": {
        "lat": 32.0998,
        "lng": 76.2691,
    },

    "MANDI": {
        "lat": 31.5892,
        "lng": 76.9182,
    },

    "SOLAN": {
        "lat": 30.9045,
        "lng": 77.0967,
    },

    "KULLU": {
        "lat": 31.9579,
        "lng": 77.1095,
    },

    # --------------------------------------------------------
    # UTTARAKHAND
    # --------------------------------------------------------

    "DEHRADUN": {
        "lat": 30.3165,
        "lng": 78.0322,
    },

    "HARIDWAR": {
        "lat": 29.9457,
        "lng": 78.1642,
    },

    "NAINITAL": {
        "lat": 29.3919,
        "lng": 79.4542,
    },

    "ALMORA": {
        "lat": 29.5971,
        "lng": 79.6591,
    },

    "PAURI_GARHWAL": {
        "lat": 30.1490,
        "lng": 78.7814,
    },

    "UDHAM_SINGH_NAGAR": {
        "lat": 28.9736,
        "lng": 79.4000,
    },

    # --------------------------------------------------------
    # GOA
    # --------------------------------------------------------

    "NORTH_GOA": {
        "lat": 15.4909,
        "lng": 73.8278,
    },

    "SOUTH_GOA": {
        "lat": 15.2736,
        "lng": 73.9581,
    },

    # --------------------------------------------------------
    # ASSAM
    # --------------------------------------------------------

    "KAMRUP_METROPOLITAN": {
        "lat": 26.1445,
        "lng": 91.7362,
    },

    "KAMRUP": {
        "lat": 26.3167,
        "lng": 91.5833,
    },

    "DIBRUGARH": {
        "lat": 27.4728,
        "lng": 94.9120,
    },

    "JORHAT": {
        "lat": 26.7509,
        "lng": 94.2037,
    },

    "SIVASAGAR": {
        "lat": 26.9826,
        "lng": 94.6425,
    },

    "SILCHAR": {
        "lat": 24.8333,
        "lng": 92.7789,
    },

    # --------------------------------------------------------
    # JAMMU & KASHMIR
    # --------------------------------------------------------

    "JAMMU": {
        "lat": 32.7266,
        "lng": 74.8570,
    },

    "SRINAGAR": {
        "lat": 34.0837,
        "lng": 74.7973,
    },

    "ANANTNAG": {
        "lat": 33.7311,
        "lng": 75.1487,
    },

    "BARAMULLA": {
        "lat": 34.1980,
        "lng": 74.3636,
    },

    "KATHUA": {
        "lat": 32.5830,
        "lng": 75.0000,
    },

    # --------------------------------------------------------
    # LADAKH
    # --------------------------------------------------------

    "LEH": {
        "lat": 34.1526,
        "lng": 77.5771,
    },

    "KARGIL": {
        "lat": 34.5539,
        "lng": 76.1349,
    },

    # --------------------------------------------------------
    # SIKKIM
    # --------------------------------------------------------

    "EAST_SIKKIM": {
        "lat": 27.3389,
        "lng": 88.6065,
    },

    "WEST_SIKKIM": {
        "lat": 27.2800,
        "lng": 88.2600,
    },

    "SOUTH_SIKKIM": {
        "lat": 27.1650,
        "lng": 88.3550,
    },

    "NORTH_SIKKIM": {
        "lat": 27.7200,
        "lng": 88.6000,
    },

    # --------------------------------------------------------
    # ARUNACHAL PRADESH
    # --------------------------------------------------------

    "PAPUMPARE": {
        "lat": 27.0844,
        "lng": 93.6053,
    },

    "EAST_SIANG": {
        "lat": 28.0667,
        "lng": 95.3333,
    },

    "WEST_SIANG": {
        "lat": 28.2167,
        "lng": 94.7667,
    },

    "TAWANG": {
        "lat": 27.5860,
        "lng": 91.8594,
    },

    # --------------------------------------------------------
    # MANIPUR
    # --------------------------------------------------------

    "IMPHAL_EAST": {
        "lat": 24.8170,
        "lng": 93.9368,
    },

    "IMPHAL_WEST": {
        "lat": 24.8170,
        "lng": 93.9368,
    },

    "THOUBAL": {
        "lat": 24.6380,
        "lng": 94.0100,
    },

    "BISHNUPUR": {
        "lat": 24.6319,
        "lng": 93.7594,
    },

    # --------------------------------------------------------
    # MEGHALAYA
    # --------------------------------------------------------

    "EAST_KHASI_HILLS": {
        "lat": 25.5788,
        "lng": 91.8933,
    },

    "WEST_KHASI_HILLS": {
        "lat": 25.3000,
        "lng": 91.2667,
    },

    "RI_BHOI": {
        "lat": 25.8700,
        "lng": 91.9000,
    },

    "EAST_GARO_HILLS": {
        "lat": 25.5144,
        "lng": 90.2028,
    },

    # --------------------------------------------------------
    # MIZORAM
    # --------------------------------------------------------

    "AIZAWL": {
        "lat": 23.7271,
        "lng": 92.7176,
    },

    "LUNGLEI": {
        "lat": 22.8894,
        "lng": 92.7470,
    },

    "CHAMPHAI": {
        "lat": 23.4650,
        "lng": 93.3280,
    },

    # --------------------------------------------------------
    # NAGALAND
    # --------------------------------------------------------

    "KOHIMA": {
        "lat": 25.6751,
        "lng": 94.1086,
    },

    "DIMAPUR": {
        "lat": 25.9063,
        "lng": 93.7273,
    },

    "MOKOKCHUNG": {
        "lat": 26.3220,
        "lng": 94.5180,
    },

    # --------------------------------------------------------
    # TRIPURA
    # --------------------------------------------------------

    "WEST_TRIPURA": {
        "lat": 23.8315,
        "lng": 91.2868,
    },

    "SEPAHIJALA": {
        "lat": 23.6500,
        "lng": 91.3000,
    },

    "SOUTH_TRIPURA": {
        "lat": 23.3000,
        "lng": 91.5000,
    },

    # --------------------------------------------------------
    # UNION TERRITORIES
    # --------------------------------------------------------

    "DELHI": {
        "lat": 28.6139,
        "lng": 77.2090,
    },

    "CHANDIGARH": {
        "lat": 30.7333,
        "lng": 76.7794,
    },

    "PUDUCHERRY": {
        "lat": 11.9416,
        "lng": 79.8083,
    },

    "LAKSHADWEEP": {
        "lat": 10.5667,
        "lng": 72.6417,
    },

    "DAMAN": {
        "lat": 20.3974,
        "lng": 72.8328,
    },

    "DIU": {
        "lat": 20.7144,
        "lng": 70.9871,
    },

    "SILVASSA": {
        "lat": 20.2733,
        "lng": 73.0080,
    },

    "PORT_BLAIR": {
        "lat": 11.6234,
        "lng": 92.7265,
    },
}


# ============================================================
# STATE CAPITAL FALLBACKS
#
# Used ONLY when a particular district isn't present in the
# static HQ dictionary.
#
# This guarantees that the Village dropdown never remains
# empty for a district.
# ============================================================

STATE_CAPITAL_COORDINATES = {

    "AP": {
        "lat": 16.5062,
        "lng": 80.6480,
    },

    "AR": {
        "lat": 27.0844,
        "lng": 93.6053,
    },

    "AS": {
        "lat": 26.1445,
        "lng": 91.7362,
    },

    "BR": {
        "lat": 25.5941,
        "lng": 85.1376,
    },

    "CG": {
        "lat": 21.2514,
        "lng": 81.6296,
    },

    "GA": {
        "lat": 15.4909,
        "lng": 73.8278,
    },

    "GJ": {
        "lat": 23.2156,
        "lng": 72.6369,
    },

    "HR": {
        "lat": 30.7333,
        "lng": 76.7794,
    },

    "HP": {
        "lat": 31.1048,
        "lng": 77.1734,
    },

    "JH": {
        "lat": 23.3441,
        "lng": 85.3096,
    },

    "KA": {
        "lat": 12.9716,
        "lng": 77.5946,
    },

    "KL": {
        "lat": 8.5241,
        "lng": 76.9366,
    },

    "MP": {
        "lat": 23.2599,
        "lng": 77.4126,
    },

    "MH": {
        "lat": 19.0760,
        "lng": 72.8777,
    },

    "MN": {
        "lat": 24.8170,
        "lng": 93.9368,
    },

    "ML": {
        "lat": 25.5788,
        "lng": 91.8933,
    },

    "MZ": {
        "lat": 23.7271,
        "lng": 92.7176,
    },

    "NL": {
        "lat": 25.6751,
        "lng": 94.1086,
    },

    "OD": {
        "lat": 20.2961,
        "lng": 85.8245,
    },

    "PB": {
        "lat": 30.7333,
        "lng": 76.7794,
    },

    "RJ": {
        "lat": 26.9124,
        "lng": 75.7873,
    },

    "SK": {
        "lat": 27.3389,
        "lng": 88.6065,
    },

    "TN": {
        "lat": 13.0827,
        "lng": 80.2707,
    },

    "TS": {
        "lat": 17.3850,
        "lng": 78.4867,
    },

    "TR": {
        "lat": 23.8315,
        "lng": 91.2868,
    },

    "UP": {
        "lat": 26.8467,
        "lng": 80.9462,
    },

    "UK": {
        "lat": 30.3165,
        "lng": 78.0322,
    },

    "WB": {
        "lat": 22.5726,
        "lng": 88.3639,
    },

    "AN": {
        "lat": 11.6234,
        "lng": 92.7265,
    },

    "CH": {
        "lat": 30.7333,
        "lng": 76.7794,
    },

    "DN": {
        "lat": 20.2733,
        "lng": 73.0080,
    },

    "DL": {
        "lat": 28.6139,
        "lng": 77.2090,
    },

    "JK": {
        "lat": 32.7266,
        "lng": 74.8570,
    },

    "LA": {
        "lat": 34.1526,
        "lng": 77.5771,
    },

    "LD": {
        "lat": 10.5667,
        "lng": 72.6417,
    },

    "PY": {
        "lat": 11.9416,
        "lng": 79.8083,
    },
}


# ============================================================
# BUILD FINAL DISTRICT DATA
# ============================================================

def build_final_district_data():

    remote_data = build_districts_from_remote_data()

    final_data = deepcopy(remote_data)

    # Preserve old district codes.
    for state_code, legacy_list in LEGACY_DISTRICTS.items():

        if state_code not in final_data:
            final_data[state_code] = []

        existing_names = {
            item["name"].strip().lower()
            for item in final_data[state_code]
        }

        for district in legacy_list:

            found = False

            for existing in final_data[state_code]:

                if (
                    existing["name"].strip().lower()
                    == district["name"].strip().lower()
                ):

                    existing["code"] = district["code"]

                    found = True

                    break

            if not found:

                final_data[state_code].append(
                    deepcopy(district)
                )

    # Fallback if remote district service is unavailable.
    if not final_data:
        final_data = deepcopy(
            LEGACY_DISTRICTS
        )

    return final_data


# ============================================================
# CREATE ONE HQ LOCATION FOR EVERY DISTRICT
#
# IMPORTANT:
# Existing village entries are NOT overwritten.
# ============================================================

def build_final_village_data(district_data):

    final_villages = deepcopy(VILLAGES)

    for state_code, district_list in district_data.items():

        for district in district_list:

            district_code = district["code"]
            district_name = district["name"]

            # Existing village data remains untouched.
            if district_code in final_villages:
                continue

            normalized_name = normalize_code(
                district_name
            )

            # First try exact static HQ coordinate.
            hq = DISTRICT_HQ_COORDINATES.get(
                normalized_name
            )

            # If not found, use state capital as
            # demo fallback.
            if hq is None:

                hq = STATE_CAPITAL_COORDINATES.get(
                    state_code
                )

            # Extremely unlikely, but if even state
            # fallback doesn't exist, skip safely.
            if hq is None:
                continue

            final_villages[district_code] = [
                {
                    "code": f"{district_code}_HQ",

                    # IMPORTANT:
                    # Frontend expects "name" from villages.
                    # We keep this compatible with existing
                    # LandMapping.jsx.
                    "name": f"{district_name} HQ",

                    "lat": hq["lat"],
                    "lng": hq["lng"],
                }
            ]

    return final_villages


# ============================================================
# FINAL DATA
# ============================================================

DISTRICTS = build_final_district_data()

FINAL_VILLAGES = build_final_village_data(
    DISTRICTS
)


# ============================================================
# FRONTEND METADATA
# ============================================================

GEOGRAPHY_DATA = {

    "states": STATES,

    "districts": DISTRICTS,

    "villages": FINAL_VILLAGES,
}


# ============================================================
# API
# ============================================================

@router.get("/metadata")
def metadata():

    return deepcopy(GEOGRAPHY_DATA)
