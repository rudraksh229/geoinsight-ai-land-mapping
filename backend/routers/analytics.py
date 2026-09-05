
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user

from services.analytics_service import (
    get_dashboard_summary,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return analytics summary for the authenticated user.
    """

    try:
        user_id = getattr(
            current_user,
            "id",
            None,
        )

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Authenticated user information is missing.",
            )

        return get_dashboard_summary(
            db=db,
            user_id=int(user_id),
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
            f"[Analytics Router] "
            f"Analytics error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate analytics summary. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
