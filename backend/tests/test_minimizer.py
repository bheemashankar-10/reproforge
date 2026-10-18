
from backend.app.engine.minimizer import minimize_input


def test_minimizes_failing_input():
    items = ["A", "B", "C", "D"]

    def still_fails(candidate):
        return "B" in candidate and "D" in candidate

    result = minimize_input(items, still_fails)

    assert result == ["B", "D"]


def test_keeps_input_when_nothing_can_be_removed():
    items = ["A", "B"]

    def still_fails(candidate):
        return len(candidate) == 2

    result = minimize_input(items, still_fails)

    assert result == ["A", "B"]
