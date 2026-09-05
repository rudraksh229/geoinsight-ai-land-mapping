
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from security import get_current_user
from services.polygon_service import analyze_polygon


router = APIRouter(
    prefix="/polygon",
    tags=["Polygon Analysis"],
)


@router.post("/upload")
async def upload_polygon(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload a polygon file and analyze the selected area.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        return analyze_polygon(
            contents
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Polygon Router] "
            f"Polygon analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Polygon analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc

    finally:
        await file.close()
