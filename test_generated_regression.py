import subprocess
import sys


def test_regression():
    result = subprocess.run(
        [sys.executable, '-I', '-c', 'def divide(a, b):\n    return a / b\n\ndivide(1, 0)'], capture_output=True, text=True, timeout=5
    )
    assert result.returncode != 0
    assert 'ZeroDivisionError' in result.stderr

