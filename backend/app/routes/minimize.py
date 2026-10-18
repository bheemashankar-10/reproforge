
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.engine.minimizer import minimize_input

router = APIRouter()


class MinimizeRequest(BaseModel):
    items: list[str] = Field(min_length=1, max_length=100)
    required_items: list[str] = Field(min_length=1, max_length=100)


@router.post("/minimize")
def minimize(request: MinimizeRequest):
    required = set(request.required_items)

    def still_fails(candidate: list[str]) -> bool:
        return required.issubset(candidate)

    result = minimize_input(request.items, still_fails)

    return {
        "original_input": request.items,
        "minimized_input": result,
        "original_size": len(request.items),
        "minimized_size": len(result),
    }
