
from collections.abc import Callable


def minimize_input(
    items: list[str],
    still_fails: Callable[[list[str]], bool],
) -> list[str]:
    """Remove unnecessary items while preserving the failure."""

    result = items.copy()
    chunk_size = max(1, len(result) // 2)

    while result and chunk_size >= 1:
        reduced = False

        for start in range(0, len(result), chunk_size):
            candidate = (
                result[:start]
                + result[start + chunk_size:]
            )

            if candidate and still_fails(candidate):
                result = candidate
                reduced = True
                break

        if not reduced:
            if chunk_size == 1:
                break
            chunk_size = max(1, chunk_size // 2)

    return result
