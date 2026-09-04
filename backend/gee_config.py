import ee
import json
import os

_is_initialized = False

def init_gee():
    global _is_initialized
    if _is_initialized:
        return

    gee_key_str = os.getenv("EE_SERVICE_ACCOUNT_KEY")

    if gee_key_str:
        try:
            # Clean string format for multiline JSON strings
            gee_key_str = gee_key_str.strip()
            key_dict = json.loads(gee_key_str)
            
            # Ensure private key handles newlines correctly
            if "private_key" in key_dict:
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

            credentials = ee.ServiceAccountCredentials(
                key_dict['client_email'],
                key_data=json.dumps(key_dict)  # Processed JSON string pass karein
            )
            ee.Initialize(credentials, project="geoinsight-ai-503616")
            _is_initialized = True
            print("GEE initialized successfully via Service Account!")
        except Exception as e:
            print(f"Service Account Init Error: {e}")
    else:
        print("WARNING: EE_SERVICE_ACCOUNT_KEY not found in Environment Variables!")