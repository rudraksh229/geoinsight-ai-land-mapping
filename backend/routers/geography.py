from fastapi import APIRouter

router = APIRouter(
    prefix="/geography",
    tags=["Geography"]
)


# ==========================================
# GEOGRAPHY DATA
# ==========================================

GEOGRAPHY_DATA = {

    "states": [
        {
            "code": "MH",
            "name": "Maharashtra"
        },
        {
            "code": "UP",
            "name": "Uttar Pradesh"
        },
        {
            "code": "MP",
            "name": "Madhya Pradesh"
        },
        {
            "code": "RJ",
            "name": "Rajasthan"
        },
        {
            "code": "GJ",
            "name": "Gujarat"
        }
    ],

    "districts": {

        "MH": [
            {
                "code": "PUNE",
                "name": "Pune"
            },
            {
                "code": "MUMBAI",
                "name": "Mumbai"
            },
            {
                "code": "NAGPUR",
                "name": "Nagpur"
            }
        ],

        "UP": [
            {
                "code": "GZB",
                "name": "Ghaziabad"
            },
            {
                "code": "LKO",
                "name": "Lucknow"
            },
            {
                "code": "AGRA",
                "name": "Agra"
            }
        ],

        "MP": [
            {
                "code": "IND",
                "name": "Indore"
            },
            {
                "code": "BPL",
                "name": "Bhopal"
            }
        ],

        "RJ": [
            {
                "code": "JPR",
                "name": "Jaipur"
            },
            {
                "code": "JOD",
                "name": "Jodhpur"
            }
        ],

        "GJ": [
            {
                "code": "AMD",
                "name": "Ahmedabad"
            },
            {
                "code": "SRT",
                "name": "Surat"
            }
        ]
    },

    "villages": {

        "PUNE": [
            {
                "code": "KHADAKWASLA",
                "name": "Khadakwasla",
                "lat": 18.5913,
                "lng": 73.7386
            },
            {
                "code": "HINJEWADI",
                "name": "Hinjewadi",
                "lat": 18.5912,
                "lng": 73.7380
            }
        ],

        "MUMBAI": [
            {
                "code": "BORIVALI",
                "name": "Borivali",
                "lat": 19.2300,
                "lng": 72.8570
            }
        ],

        "NAGPUR": [
            {
                "code": "KORADI",
                "name": "Koradi",
                "lat": 21.2500,
                "lng": 79.1000
            }
        ],

        "GZB": [
            {
                "code": "LOHIA",
                "name": "Loni",
                "lat": 28.7500,
                "lng": 77.2900
            }
        ],

        "LKO": [
            {
                "code": "MALIHABAD",
                "name": "Malihabad",
                "lat": 26.9220,
                "lng": 80.7100
            }
        ],

        "AGRA": [
            {
                "code": "FATEHPUR",
                "name": "Fatehpur Sikri",
                "lat": 27.0945,
                "lng": 77.6600
            }
        ],

        "IND": [
            {
                "code": "MHOW",
                "name": "Mhow",
                "lat": 22.5500,
                "lng": 75.7600
            }
        ],

        "BPL": [
            {
                "code": "SEHORE",
                "name": "Sehore",
                "lat": 23.2000,
                "lng": 77.0800
            }
        ],

        "JPR": [
            {
                "code": "AMBER",
                "name": "Amer",
                "lat": 26.9855,
                "lng": 75.8513
            }
        ],

        "JOD": [
            {
                "code": "MANDORE",
                "name": "Mandore",
                "lat": 26.3540,
                "lng": 73.0480
            }
        ],

        "AMD": [
            {
                "code": "SANAND",
                "name": "Sanand",
                "lat": 22.9920,
                "lng": 72.3810
            }
        ],

        "SRT": [
            {
                "code": "KAMREJ",
                "name": "Kamrej",
                "lat": 21.2700,
                "lng": 72.9600
            }
        ]
    }
}


# ==========================================
# GET GEOGRAPHY METADATA
# ==========================================

@router.get("/metadata")
def metadata():

    return GEOGRAPHY_DATA