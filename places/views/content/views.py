import logging
from typing import Optional

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from places.errors import APIError, NotFound
from places.state import app_state

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/places")
async def get_places(
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    locale: str = Query("ru"),
):
    try:
        places = await app_state.content_repo.get_places(
            category_id=category_id,
            limit=limit,
            offset=offset,
            locale=locale,
        )
        return {"places": places}

    except NotFound as e:
        logger.warning(f"NotFound: {e}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": e.status, "message": str(e)},
        )

    except APIError as e:
        logger.warning(f"APIError: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": e.status, "message": str(e)},
        )

    except Exception as e:
        logger.error(f"Failed to get places: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "internal_error",
                "message": "Internal server error",
            },
        )
