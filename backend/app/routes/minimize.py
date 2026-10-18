from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.db import save_run
from backend.app.engine.ddmin import ddmin

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
        return required.issubset(subset)

    if not fails(req.items):
        raise HTTPException(
            status_code=400,
            detail="The original items do not contain all required items, so there is no failure to minimize.",
        )

    minimized, tests = ddmin(req.items, fails)
    response = MinimizeResponse(
        original_input=req.items,
        minimized_input=minimized,
        original_size=len(req.items),
        minimized_size=len(minimized),
        tests_run=tests,
    )
    save_run("minimize", req.model_dump(), response.model_dump())
    return response
