from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..engine.ddmin import ddmin

router = APIRouter()


class MinimizeRequest(BaseModel):
    items: list[str] = Field(min_length=1, max_length=200)
    required_items: list[str] = Field(min_length=1, max_length=200)


class MinimizeResponse(BaseModel):
    original_input: list[str]
    minimized_input: list[str]
    original_size: int
    minimized_size: int
    tests_run: int


@router.post("/minimize", response_model=MinimizeResponse)
def minimize(req: MinimizeRequest):
    required = set(req.required_items)

    def fails(subset: list[str]) -> bool:
        # The "bug" appears whenever every required item is present
        return required.issubset(subset)

    if not fails(req.items):
        raise HTTPException(
            status_code=400,
            detail="The original items don't contain all required items, so there is no failure to minimize.",
        )

    minimized, tests = ddmin(req.items, fails)
    return MinimizeResponse(
        original_input=req.items,
        minimized_input=minimized,
        original_size=len(req.items),
        minimized_size=len(minimized),
        tests_run=tests,
    )