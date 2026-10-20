
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(
    app,
    headers={"X-API-Key": "reproforge-test-key"},
)


def test_reproduce_endpoint():
    response = client.post(
        "/reproduce",
        json={
            "code": "print('Hello ReproForge')",
            "timeout": 5,
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["stdout"] == "Hello ReproForge\n"


def test_minimize_endpoint():
    response = client.post(
        "/minimize",
        json={
            "items": ["A", "B", "C", "D"],
            "required_items": ["B", "D"],
        },
    )

    assert response.status_code == 200
    assert response.json()["minimized_input"] == ["B", "D"]
    assert response.json()["minimized_size"] == 2

def test_generate_test_endpoint():
    response = client.post(
        "/generate-test",
        json={
            "code": "print(1 / 0)",
            "expected_error": "ZeroDivisionError",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"] == "python"
    assert data["framework"] == "pytest"
    assert "def test_regression():" in data["test_code"]
    assert "ZeroDivisionError" in data["test_code"]
