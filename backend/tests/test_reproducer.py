import time
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

def test_environment_variables_are_isolated():
    code = (
        "import os; "
        "print(os.environ.get('API_KEY')); "
        "print(os.environ.get('MONGODB_URI'))"
    )

    result = reproduce_bug(code)

    assert result["success"] is True
    assert result["stdout"] == "None\nNone\n"

def test_network_access_is_blocked():
    code = (
        "import urllib.request; "
        "urllib.request.urlopen('https://example.com', timeout=3)"
    )

    result = reproduce_bug(code)

    assert result["success"] is False
    assert "URLError" in result["stderr"]
    assert result["returncode"] != 0
def test_excessive_output_is_limited():
    code = "while True: print('A' * 1000)"

    result = reproduce_bug(code, timeout=2)

    assert result["success"] is False
    assert len(result["stdout"]) + len(result["stderr"]) <= 1_100_000
    assert "output limit" in result["stderr"].lower()
def test_excessive_output_is_limited():
    code = "while True: print('A' * 1000)"

    start = time.monotonic()
    result = reproduce_bug(code, timeout=10)
    elapsed = time.monotonic() - start

    assert result["success"] is False
    assert len(result["stdout"].encode()) <= 1_000_000
    assert "output limit" in result["stderr"].lower()
    assert elapsed < 10