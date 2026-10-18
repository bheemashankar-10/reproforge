
from backend.app.engine.test_generator import generate_regression_test


def test_generates_success_test():
    test_code = generate_regression_test(
        "print('Hello')"
    )

    assert "def test_regression():" in test_code
    assert "assert result.returncode == 0" in test_code


def test_generates_error_test():
    test_code = generate_regression_test(
        "print(1 / 0)",
        expected_error="ZeroDivisionError",
    )

    assert "def test_regression():" in test_code
    assert "ZeroDivisionError" in test_code
    assert "assert" in test_code
