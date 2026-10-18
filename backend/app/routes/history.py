from fastapi import APIRouter, HTTPException

from ..db import list_runs

router = APIRouter()


@router.get("/history")
def history(limit: int = 20):
    try:
        return list_runs(min(max(limit, 1), 100))
    except Exception:
        raise HTTPException(status_code=503, detail="History database unavailable")