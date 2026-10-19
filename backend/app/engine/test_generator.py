
def generate_regression_test(
    code: str,
    expected_error: str | None = None,
) -> str:
    """Generate a pytest test for a reproducible Python program."""

    if expected_error:
        return (
            "import subprocess\n"
            "import sys\n\n\n"
            "def test_regression():\n"
            "    result = subprocess.run(\n"
            "        [sys.executable, '-I', '-c', "
            + repr(code)
            + "], capture_output=True, text=True, timeout=5\n"
            "    )\n"
            "    assert result.returncode != 0\n"
            "    assert "
            + repr(expected_error)
            + " in result.stderr\n"
        )

    return (
        "import subprocess\n"
        "import sys\n\n\n"
        "def test_regression():\n"
        "    result = subprocess.run(\n"
        "        [sys.executable, '-I', '-c', "
        + repr(code)
        + "], capture_output=True, text=True, timeout=5\n"
        "    )\n"
        "    assert result.returncode == 0\n"
    )
