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
            # Clean string format
            gee_key_str = gee_key_str.strip()
            
            # JSON parsing with strict=False to handle potential control characters
            key_dict = json.loads(gee_key_str, strict=False)
            
            # Fix newline breaks in private key
            if "private_key" in key_dict and isinstance(key_dict["private_key"], str):
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

            # Correct GEE Credentials Initialization using raw dict
            credentials = ee.ServiceAccountCredentials(
                email=key_dict.get('client_email'),
                key_data=key_dict.get('private_key') # Direct private_key string accept karta hai
            )
            
            ee.Initialize(credentials, project="geoinsight-ai-503616")
            _is_initialized = True
            print("GEE initialized successfully via Service Account!")
            
        except Exception as e:
            print(f"Service Account Init Error: {e}")
            # Crash hone se bachane ke liye safe fallback attempt
            try:
                ee.Initialize(project="geoinsight-ai-503616")
                _is_initialized = True
                print("GEE initialized via Default Application Credentials!")
            except Exception as fallback_err:
                print(f"Fallback GEE Init failed: {fallback_err}")
    else:
        print("WARNING: EE_SERVICE_ACCOUNT_KEY not found in Environment Variables!")
        try:
            ee.Initialize(project="geoinsight-ai-503616")
            _is_initialized = True
        except Exception as err:
            print(f"Default GEE Init Error: {err}")
