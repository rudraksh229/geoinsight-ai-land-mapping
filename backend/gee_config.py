import ee
import json
import os
import threading

_is_initialized = False
_init_lock = threading.Lock()

GEE_PROJECT_ID = "geoinsight-ai-503616"


def init_gee():
    global _is_initialized

    if _is_initialized:
        return

    with _init_lock:
        if _is_initialized:
            return

        gee_key_str = os.getenv("EE_SERVICE_ACCOUNT_KEY")

        if not gee_key_str:
            raise RuntimeError(
                "EE_SERVICE_ACCOUNT_KEY environment variable is not set."
            )

        try:
            # Render environment variables may sometimes be entered
            # with surrounding single/double quotes.
            gee_key_str = gee_key_str.strip()

            if (
                len(gee_key_str) >= 2
                and gee_key_str[0] == gee_key_str[-1]
                and gee_key_str[0] in ("'", '"')
            ):
                gee_key_str = gee_key_str[1:-1].strip()

            key_dict = json.loads(gee_key_str, strict=False)

            required_fields = [
                "client_email",
                "private_key",
                "project_id",
            ]

            missing_fields = [
                field for field in required_fields
                if not key_dict.get(field)
            ]

            if missing_fields:
                raise RuntimeError(
                    f"Invalid Earth Engine service-account JSON. "
                    f"Missing: {', '.join(missing_fields)}"
                )

            private_key = key_dict["private_key"]

            # Convert escaped newlines into real newlines.
            private_key = private_key.replace("\\n", "\n")

            credentials = ee.ServiceAccountCredentials(
                email=key_dict["client_email"],
                key_data=private_key,
            )

            ee.Initialize(
                credentials=credentials,
                project=GEE_PROJECT_ID,
            )

            _is_initialized = True

            print(
                f"GEE initialized successfully using service account "
                f"for project: {GEE_PROJECT_ID}"
            )

        except Exception as exc:
            _is_initialized = False

            raise RuntimeError(
                f"Google Earth Engine initialization failed: {exc}"
            ) from exc
