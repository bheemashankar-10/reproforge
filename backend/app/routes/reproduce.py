
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.engine.reproducer import reproduce_bug

router = APIRouter()


class ReproduceRequest(BaseModel):
    code: str = Field(min_length=1, max_length=10000)
    timeout: int = Field(default=5, ge=1, le=10)


@router.post("/reproduce")
def reproduce(request: ReproduceRequest):
    return reproduce_bug(request.code, request.timeout)
