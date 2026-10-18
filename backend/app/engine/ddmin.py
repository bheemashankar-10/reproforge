from math import ceil
from typing import Callable


def ddmin(items: list, fails: Callable[[list], bool]) -> tuple[list, int]:
    """Shrink `items` to a smaller list that still makes `fails` return True.

    Returns (minimized_items, number_of_tests_run).
    """
    items = list(items)
    n = 2
    tests = 0

    while len(items) >= 2:
        chunk = ceil(len(items) / n)
        subsets = [items[i:i + chunk] for i in range(0, len(items), chunk)]
        reduced = False

        # 1) Try each chunk on its own
        for subset in subsets:
            tests += 1
            if fails(subset):
                items, n, reduced = subset, 2, True
                break

        # 2) Try removing each chunk (keep the complement)
        if not reduced:
            for i in range(len(subsets)):
                complement = [x for j, s in enumerate(subsets) if j != i for x in s]
                tests += 1
                if fails(complement):
                    items, n, reduced = complement, max(n - 1, 2), True
                    break

        # 3) Nothing worked: split finer, or stop
        if not reduced:
            if n >= len(items):
                break
            n = min(len(items), n * 2)

    return items, tests