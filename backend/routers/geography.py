from copy import deepcopy

from fastapi import APIRouter


router = APIRouter(
    prefix="/geography",
    tags=["Geography"],
)


# ============================================================
# GEOGRAPHY DATA
# ============================================================

GEOGRAPHY_DATA = {
    "states": [
        {
            "code": "MH",
            "name": "Maharashtra",
        },
        {
            "code": "UP",
            "name": "Uttar Pradesh",
        },
        {
            "code": "MP",
            "name": "Madhya Pradesh",
        },
        {
            "code": "RJ",
            "name": "Rajasthan",
        },
        {
            "code": "GJ",
            "name": "Gujarat",
        },
    ],

    # ========================================================
    # DISTRICTS
    # ========================================================

    "districts": {
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

        "UP": [
            {
                "code": "AGRA",
                "name": "Agra",
            },
            {
                "code": "ALIGARH",
                "name": "Aligarh",
            },
            {
                "code": "AMBEDKAR_NAGAR",
                "name": "Ambedkar Nagar",
            },
            {
                "code": "AMETHI",
                "name": "Amethi",
            },
            {
                "code": "AMROHA",
                "name": "Amroha",
            },
            {
                "code": "AURAIYA",
                "name": "Auraiya",
            },
            {
                "code": "AYODHYA",
                "name": "Ayodhya",
            },
            {
                "code": "AZAMGARH",
                "name": "Azamgarh",
            },
            {
                "code": "BAGHPAT",
                "name": "Baghpat",
            },
            {
                "code": "BAHRAICH",
                "name": "Bahraich",
            },
            {
                "code": "BALLIA",
                "name": "Ballia",
            },
            {
                "code": "BALRAMPUR",
                "name": "Balrampur",
            },
            {
                "code": "BANDA",
                "name": "Banda",
            },
            {
                "code": "BARABANKI",
                "name": "Barabanki",
            },
            {
                "code": "BAREILLY",
                "name": "Bareilly",
            },
            {
                "code": "BASTI",
                "name": "Basti",
            },
            {
                "code": "BHADOHI",
                "name": "Bhadohi",
            },
            {
                "code": "BIJNOR",
                "name": "Bijnor",
            },
            {
                "code": "BUDAUN",
                "name": "Budaun",
            },
            {
                "code": "BULANDSHAHR",
                "name": "Bulandshahr",
            },
            {
                "code": "CHANDAULI",
                "name": "Chandauli",
            },
            {
                "code": "CHITRAKOOT",
                "name": "Chitrakoot",
            },
            {
                "code": "DEORIA",
                "name": "Deoria",
            },
            {
                "code": "ETAH",
                "name": "Etah",
            },
            {
                "code": "ETAWAH",
                "name": "Etawah",
            },
            {
                "code": "FARRUKHABAD",
                "name": "Farrukhabad",
            },
            {
                "code": "FATEHPUR",
                "name": "Fatehpur",
            },
            {
                "code": "FIROZABAD",
                "name": "Firozabad",
            },
            {
                "code": "GAUTAM_BUDDHA_NAGAR",
                "name": "Gautam Buddha Nagar",
            },
            {
                "code": "GHAZIABAD",
                "name": "Ghaziabad",
            },
            {
                "code": "GHAZIPUR",
                "name": "Ghazipur",
            },
            {
                "code": "GONDA",
                "name": "Gonda",
            },
            {
                "code": "GORAKHPUR",
                "name": "Gorakhpur",
            },
            {
                "code": "HAMIRPUR",
                "name": "Hamirpur",
            },
            {
                "code": "HAPUR",
                "name": "Hapur",
            },
            {
                "code": "HARDOI",
                "name": "Hardoi",
            },
            {
                "code": "HATHRAS",
                "name": "Hathras",
            },
            {
                "code": "JALAUN",
                "name": "Jalaun",
            },
            {
                "code": "JAUNPUR",
                "name": "Jaunpur",
            },
            {
                "code": "JHANSI",
                "name": "Jhansi",
            },
            {
                "code": "KANNAUJ",
                "name": "Kannauj",
            },
            {
                "code": "KANPUR_DEHAT",
                "name": "Kanpur Dehat",
            },
            {
                "code": "KANPUR_NAGAR",
                "name": "Kanpur Nagar",
            },
            {
                "code": "KASGANJ",
                "name": "Kasganj",
            },
            {
                "code": "KAUSHAMBI",
                "name": "Kaushambi",
            },
            {
                "code": "KUSHINAGAR",
                "name": "Kushinagar",
            },
            {
                "code": "LAKHIMPUR_KHERI",
                "name": "Lakhimpur Kheri",
            },
            {
                "code": "LALITPUR",
                "name": "Lalitpur",
            },
            {
                "code": "LKO",
                "name": "Lucknow",
            },
            {
                "code": "MAHARAJGANJ",
                "name": "Maharajganj",
            },
            {
                "code": "MAHOBA",
                "name": "Mahoba",
            },
            {
                "code": "MAINPURI",
                "name": "Mainpuri",
            },
            {
                "code": "MATHURA",
                "name": "Mathura",
            },
            {
                "code": "MAU",
                "name": "Mau",
            },
            {
                "code": "MEERUT",
                "name": "Meerut",
            },
            {
                "code": "MIRZAPUR",
                "name": "Mirzapur",
            },
            {
                "code": "MORADABAD",
                "name": "Moradabad",
            },
            {
                "code": "MUZAFFARNAGAR",
                "name": "Muzaffarnagar",
            },
            {
                "code": "PILIBHIT",
                "name": "Pilibhit",
            },
            {
                "code": "PRATAPGARH",
                "name": "Pratapgarh",
            },
            {
                "code": "PRAYAGRAJ",
                "name": "Prayagraj",
            },
            {
                "code": "RAEBARELI",
                "name": "Raebareli",
            },
            {
                "code": "RAMPUR",
                "name": "Rampur",
            },
            {
                "code": "SAHARANPUR",
                "name": "Saharanpur",
            },
            {
                "code": "SAMBHAL",
                "name": "Sambhal",
            },
            {
                "code": "SANT_KABIR_NAGAR",
                "name": "Sant Kabir Nagar",
            },
            {
                "code": "SHAHJAHANPUR",
                "name": "Shahjahanpur",
            },
            {
                "code": "SHAMLI",
                "name": "Shamli",
            },
            {
                "code": "SHRAVASTI",
                "name": "Shravasti",
            },
            {
                "code": "SIDDHARTHNAGAR",
                "name": "Siddharthnagar",
            },
            {
                "code": "SITAPUR",
                "name": "Sitapur",
            },
            {
                "code": "SONBHADRA",
                "name": "Sonbhadra",
            },
            {
                "code": "SULTANPUR",
                "name": "Sultanpur",
            },
            {
                "code": "UNNAO",
                "name": "Unnao",
            },
            {
                "code": "VARANASI",
                "name": "Varanasi",
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
    },

    # ========================================================
    # VILLAGES / ANALYSIS LOCATIONS
    # ========================================================

    "villages": {

        # ----------------------------------------------------
        # MAHARASHTRA
        # ----------------------------------------------------

        "PUNE": [
            {
                "code": "KHADAKWASLA",
                "name": "Khadakwasla",
                "lat": 18.5913,
                "lng": 73.7386,
            },
            {
                "code": "HINJEWADI",
                "name": "Hinjewadi",
                "lat": 18.5912,
                "lng": 73.7380,
            },
        ],

        "MUMBAI": [
            {
                "code": "BORIVALI",
                "name": "Borivali",
                "lat": 19.2300,
                "lng": 72.8570,
            },
        ],

        "NAGPUR": [
            {
                "code": "KORADI",
                "name": "Koradi",
                "lat": 21.2500,
                "lng": 79.1000,
            },
        ],

        # ----------------------------------------------------
        # UTTAR PRADESH
        # ----------------------------------------------------

        "AGRA": [
            {
                "code": "FATEHPUR",
                "name": "Fatehpur Sikri",
                "lat": 27.0945,
                "lng": 77.6600,
            },
        ],

        "ALIGARH": [
            {
                "code": "ALIGARH_HQ",
                "name": "Aligarh",
                "lat": 27.8974,
                "lng": 78.0880,
            },
        ],

        "AMBEDKAR_NAGAR": [
            {
                "code": "AKBARPUR",
                "name": "Akbarpur",
                "lat": 26.4290,
                "lng": 82.5340,
            },
        ],

        "AMETHI": [
            {
                "code": "GAURIGANJ",
                "name": "Gauriganj",
                "lat": 26.1610,
                "lng": 81.8070,
            },
        ],

        "AMROHA": [
            {
                "code": "AMROHA_HQ",
                "name": "Amroha",
                "lat": 28.9030,
                "lng": 78.4698,
            },
        ],

        "AURAIYA": [
            {
                "code": "AURAIYA_HQ",
                "name": "Auraiya",
                "lat": 26.4667,
                "lng": 79.5167,
            },
        ],

        "AYODHYA": [
            {
                "code": "AYODHYA_HQ",
                "name": "Ayodhya",
                "lat": 26.7990,
                "lng": 82.2040,
            },
        ],

        "AZAMGARH": [
            {
                "code": "AZAMGARH_HQ",
                "name": "Azamgarh",
                "lat": 26.0670,
                "lng": 83.1830,
            },
        ],

        "BAGHPAT": [
            {
                "code": "BAGHPAT_HQ",
                "name": "Baghpat",
                "lat": 28.9440,
                "lng": 77.2190,
            },
        ],

        "BAHRAICH": [
            {
                "code": "BAHRAICH_HQ",
                "name": "Bahraich",
                "lat": 27.5740,
                "lng": 81.5940,
            },
        ],

        "BALLIA": [
            {
                "code": "BALLIA_HQ",
                "name": "Ballia",
                "lat": 25.7580,
                "lng": 84.1490,
            },
        ],

        "BALRAMPUR": [
            {
                "code": "BALRAMPUR_HQ",
                "name": "Balrampur",
                "lat": 27.4300,
                "lng": 82.1800,
            },
        ],

        "BANDA": [
            {
                "code": "BANDA_HQ",
                "name": "Banda",
                "lat": 25.4750,
                "lng": 80.3350,
            },
        ],

        "BARABANKI": [
            {
                "code": "BARABANKI_HQ",
                "name": "Barabanki",
                "lat": 26.9300,
                "lng": 81.1900,
            },
        ],

        "BAREILLY": [
            {
                "code": "BAREILLY_HQ",
                "name": "Bareilly",
                "lat": 28.3670,
                "lng": 79.4300,
            },
        ],

        "BASTI": [
            {
                "code": "BASTI_HQ",
                "name": "Basti",
                "lat": 26.8000,
                "lng": 82.7330,
            },
        ],

        "BHADOHI": [
            {
                "code": "BHADOHI_HQ",
                "name": "Bhadohi",
                "lat": 25.3950,
                "lng": 82.5700,
            },
        ],

        "BIJNOR": [
            {
                "code": "BIJNOR_HQ",
                "name": "Bijnor",
                "lat": 29.3730,
                "lng": 78.1350,
            },
        ],

        "BUDAUN": [
            {
                "code": "BUDAUN_HQ",
                "name": "Budaun",
                "lat": 28.0330,
                "lng": 79.1200,
            },
        ],

        "BULANDSHAHR": [
            {
                "code": "BULANDSHAHR_HQ",
                "name": "Bulandshahr",
                "lat": 28.4070,
                "lng": 77.8498,
            },
        ],

        "CHANDAULI": [
            {
                "code": "CHANDAULI_HQ",
                "name": "Chandauli",
                "lat": 25.2600,
                "lng": 83.2700,
            },
        ],

        "CHITRAKOOT": [
            {
                "code": "KARWI",
                "name": "Karwi",
                "lat": 25.2000,
                "lng": 80.9000,
            },
        ],

        "DEORIA": [
            {
                "code": "DEORIA_HQ",
                "name": "Deoria",
                "lat": 26.5020,
                "lng": 83.7790,
            },
        ],

        "ETAH": [
            {
                "code": "ETAH_HQ",
                "name": "Etah",
                "lat": 27.5580,
                "lng": 78.6630,
            },
        ],

        "ETAWAH": [
            {
                "code": "ETAWAH_HQ",
                "name": "Etawah",
                "lat": 26.7850,
                "lng": 79.0150,
            },
        ],

        "FARRUKHABAD": [
            {
                "code": "FATEHGARH",
                "name": "Fatehgarh",
                "lat": 27.3650,
                "lng": 79.6400,
            },
        ],

        "FATEHPUR": [
            {
                "code": "FATEHPUR_HQ",
                "name": "Fatehpur",
                "lat": 25.9300,
                "lng": 80.8100,
            },
        ],

        "FIROZABAD": [
            {
                "code": "FIROZABAD_HQ",
                "name": "Firozabad",
                "lat": 27.1500,
                "lng": 78.3950,
            },
        ],

        "GAUTAM_BUDDHA_NAGAR": [
            {
                "code": "NOIDA",
                "name": "Noida",
                "lat": 28.5355,
                "lng": 77.3910,
            },
        ],

        "GHAZIABAD": [
            {
                "code": "GHAZIABAD_HQ",
                "name": "Ghaziabad",
                "lat": 28.6692,
                "lng": 77.4538,
            },
        ],

        "GZB": [
            {
                "code": "LOHIA",
                "name": "Loni",
                "lat": 28.7500,
                "lng": 77.2900,
            },
        ],

        "GHAZIPUR": [
            {
                "code": "GHAZIPUR_HQ",
                "name": "Ghazipur",
                "lat": 25.5800,
                "lng": 83.5800,
            },
        ],

        "GONDA": [
            {
                "code": "GONDA_HQ",
                "name": "Gonda",
                "lat": 27.1300,
                "lng": 81.9500,
            },
        ],

        "GORAKHPUR": [
            {
                "code": "GORAKHPUR_HQ",
                "name": "Gorakhpur",
                "lat": 26.7606,
                "lng": 83.3732,
            },
        ],

        "HAMIRPUR": [
            {
                "code": "HAMIRPUR_HQ",
                "name": "Hamirpur",
                "lat": 25.9550,
                "lng": 80.1500,
            },
        ],

        "HAPUR": [
            {
                "code": "HAPUR_HQ",
                "name": "Hapur",
                "lat": 28.7300,
                "lng": 77.7800,
            },
        ],

        "HARDOI": [
            {
                "code": "HARDOI_HQ",
                "name": "Hardoi",
                "lat": 27.3980,
                "lng": 80.1250,
            },
        ],

        "HATHRAS": [
            {
                "code": "HATHRAS_HQ",
                "name": "Hathras",
                "lat": 27.5950,
                "lng": 78.0520,
            },
        ],

        "JALAUN": [
            {
                "code": "ORAI",
                "name": "Orai",
                "lat": 25.9900,
                "lng": 79.4500,
            },
        ],

        "JAUNPUR": [
            {
                "code": "JAUNPUR_HQ",
                "name": "Jaunpur",
                "lat": 25.7500,
                "lng": 82.6800,
            },
        ],

        "JHANSI": [
            {
                "code": "JHANSI_HQ",
                "name": "Jhansi",
                "lat": 25.4484,
                "lng": 78.5685,
            },
        ],

        "KANNAUJ": [
            {
                "code": "KANNAUJ_HQ",
                "name": "Kannauj",
                "lat": 27.0550,
                "lng": 79.9180,
            },
        ],

        "KANPUR_DEHAT": [
            {
                "code": "AKBARPUR_KD",
                "name": "Akbarpur",
                "lat": 26.4400,
                "lng": 79.9500,
            },
        ],

        "KANPUR_NAGAR": [
            {
                "code": "KANPUR",
                "name": "Kanpur",
                "lat": 26.4499,
                "lng": 80.3319,
            },
        ],

        "KASGANJ": [
            {
                "code": "KASGANJ_HQ",
                "name": "Kasganj",
                "lat": 27.8080,
                "lng": 78.6460,
            },
        ],

        "KAUSHAMBI": [
            {
                "code": "MANJHANPUR",
                "name": "Manjhanpur",
                "lat": 25.5300,
                "lng": 81.3800,
            },
        ],

        "KUSHINAGAR": [
            {
                "code": "PADRAUNA",
                "name": "Padrauna",
                "lat": 26.9000,
                "lng": 83.9700,
            },
        ],

        "LAKHIMPUR_KHERI": [
            {
                "code": "LAKHIMPUR",
                "name": "Lakhimpur",
                "lat": 27.9500,
                "lng": 80.7800,
            },
        ],

        "LALITPUR": [
            {
                "code": "LALITPUR_HQ",
                "name": "Lalitpur",
                "lat": 24.6900,
                "lng": 78.4100,
            },
        ],

        "LKO": [
            {
                "code": "MALIHABAD",
                "name": "Malihabad",
                "lat": 26.9220,
                "lng": 80.7100,
            },
        ],

        "MAHARAJGANJ": [
            {
                "code": "MAHARAJGANJ_HQ",
                "name": "Maharajganj",
                "lat": 27.1300,
                "lng": 83.5600,
            },
        ],

        "MAHOBA": [
            {
                "code": "MAHOBA_HQ",
                "name": "Mahoba",
                "lat": 25.2900,
                "lng": 79.8700,
            },
        ],

        "MAINPURI": [
            {
                "code": "MAINPURI_HQ",
                "name": "Mainpuri",
                "lat": 27.2350,
                "lng": 79.0100,
            },
        ],

        "MATHURA": [
            {
                "code": "MATHURA_HQ",
                "name": "Mathura",
                "lat": 27.4924,
                "lng": 77.6737,
            },
        ],

        "MAU": [
            {
                "code": "MAU_HQ",
                "name": "Mau",
                "lat": 25.9400,
                "lng": 83.5600,
            },
        ],

        "MEERUT": [
            {
                "code": "MEERUT_HQ",
                "name": "Meerut",
                "lat": 28.9845,
                "lng": 77.7064,
            },
        ],

        "MIRZAPUR": [
            {
                "code": "MIRZAPUR_HQ",
                "name": "Mirzapur",
                "lat": 25.1460,
                "lng": 82.5700,
            },
        ],

        "MORADABAD": [
            {
                "code": "MORADABAD_HQ",
                "name": "Moradabad",
                "lat": 28.8389,
                "lng": 78.7768,
            },
        ],

        "MUZAFFARNAGAR": [
            {
                "code": "MUZAFFARNAGAR_HQ",
                "name": "Muzaffarnagar",
                "lat": 29.4727,
                "lng": 77.7085,
            },
        ],

        "PILIBHIT": [
            {
                "code": "PILIBHIT_HQ",
                "name": "Pilibhit",
                "lat": 28.6200,
                "lng": 79.8100,
            },
        ],

        "PRATAPGARH": [
            {
                "code": "PRATAPGARH_HQ",
                "name": "Pratapgarh",
                "lat": 25.9000,
                "lng": 81.9500,
            },
        ],

        "PRAYAGRAJ": [
            {
                "code": "PRAYAGRAJ_HQ",
                "name": "Prayagraj",
                "lat": 25.4358,
                "lng": 81.8463,
            },
        ],

        "RAEBARELI": [
            {
                "code": "RAEBARELI_HQ",
                "name": "Raebareli",
                "lat": 26.2300,
                "lng": 81.2400,
            },
        ],

        "RAMPUR": [
            {
                "code": "RAMPUR_HQ",
                "name": "Rampur",
                "lat": 28.8100,
                "lng": 79.0200,
            },
        ],

        "SAHARANPUR": [
            {
                "code": "SAHARANPUR_HQ",
                "name": "Saharanpur",
                "lat": 29.9680,
                "lng": 77.5550,
            },
        ],

        "SAMBHAL": [
            {
                "code": "SAMBHAL_HQ",
                "name": "Sambhal",
                "lat": 28.5840,
                "lng": 78.5700,
            },
        ],

        "SANT_KABIR_NAGAR": [
            {
                "code": "KHALILABAD",
                "name": "Khalilabad",
                "lat": 26.7700,
                "lng": 83.0700,
            },
        ],

        "SHAHJAHANPUR": [
            {
                "code": "SHAHJAHANPUR_HQ",
                "name": "Shahjahanpur",
                "lat": 27.8800,
                "lng": 79.9100,
            },
        ],

        "SHAMLI": [
            {
                "code": "SHAMLI_HQ",
                "name": "Shamli",
                "lat": 29.4500,
                "lng": 77.3100,
            },
        ],

        "SHRAVASTI": [
            {
                "code": "BHINGA",
                "name": "Bhinga",
                "lat": 27.7167,
                "lng": 81.9333,
            },
        ],

        "SIDDHARTHNAGAR": [
            {
                "code": "NAUGARH",
                "name": "Naugarh",
                "lat": 27.0800,
                "lng": 83.1100,
            },
        ],

        "SITAPUR": [
            {
                "code": "SITAPUR_HQ",
                "name": "Sitapur",
                "lat": 27.5700,
                "lng": 80.6800,
            },
        ],

        "SONBHADRA": [
            {
                "code": "ROBERTSGANJ",
                "name": "Robertsganj",
                "lat": 24.6900,
                "lng": 83.0700,
            },
        ],

        "SULTANPUR": [
            {
                "code": "SULTANPUR_HQ",
                "name": "Sultanpur",
                "lat": 26.2600,
                "lng": 82.0700,
            },
        ],

        "UNNAO": [
            {
                "code": "UNNAO_HQ",
                "name": "Unnao",
                "lat": 26.5500,
                "lng": 80.4900,
            },
        ],

        "VARANASI": [
            {
                "code": "VARANASI_HQ",
                "name": "Varanasi",
                "lat": 25.3176,
                "lng": 82.9739,
            },
        ],

        # ----------------------------------------------------
        # MADHYA PRADESH
        # ----------------------------------------------------

        "IND": [
            {
                "code": "MHOW",
                "name": "Mhow",
                "lat": 22.5500,
                "lng": 75.7600,
            },
        ],

        "BPL": [
            {
                "code": "SEHORE",
                "name": "Sehore",
                "lat": 23.2000,
                "lng": 77.0800,
            },
        ],

        # ----------------------------------------------------
        # RAJASTHAN
        # ----------------------------------------------------

        "JPR": [
            {
                "code": "AMBER",
                "name": "Amer",
                "lat": 26.9855,
                "lng": 75.8513,
            },
        ],

        "JOD": [
            {
                "code": "MANDORE",
                "name": "Mandore",
                "lat": 26.3540,
                "lng": 73.0480,
            },
        ],

        # ----------------------------------------------------
        # GUJARAT
        # ----------------------------------------------------

        "AMD": [
            {
                "code": "SANAND",
                "name": "Sanand",
                "lat": 22.9920,
                "lng": 72.3810,
            },
        ],

        "SRT": [
            {
                "code": "KAMREJ",
                "name": "Kamrej",
                "lat": 21.2700,
                "lng": 72.9600,
            },
        ],
    },
}


# ============================================================
# GET GEOGRAPHY METADATA
# ============================================================

@router.get("/metadata")
def metadata():
    """
    Return state, district and location metadata
    used by the frontend location selectors.
    """

    return deepcopy(GEOGRAPHY_DATA)
