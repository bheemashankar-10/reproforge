
from backend.app.engine.reproducer import reproduce_bug


def test_successful_code():
    result = reproduce_bug("print('Hello ReproForge')")

    assert result["success"] is True
    assert result["stdout"] == "Hello ReproForge\n"
    assert result["returncode"] == 0


def test_python_error():
    result = reproduce_bug("print(1 / 0)")

    assert result["success"] is False
    assert "ZeroDivisionError" in result["stderr"]
    assert result["returncode"] != 0


def test_timeout():
    result = reproduce_bug("while True: pass", timeout=1)

    assert result["success"] is False
    assert "timed out" in result["stderr"].lower()
    assert result["returncode"] is None
