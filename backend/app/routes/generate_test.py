from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.db import save_run
from backend.app.engine.test_generator import generate_regression_test

router = APIRouter()


class GenerateTestRequest(BaseModel):
    code: str = Field(min_length=1, max_length=10000)
    expected_error: str | None = Field(default=None, max_length=200)


@router.post("/generate-test")
def generate_test(request: GenerateTestRequest):
    test_code = generate_regression_test(
        request.code,
        request.expected_error,
    )

    response = {
        "test_code": test_code,
        "language": "python",
        "framework": "pytest",
    }
    save_run("generate_test", request.model_dump(), response)
    return response
