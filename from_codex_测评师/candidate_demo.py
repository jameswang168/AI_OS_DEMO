"""
Demo candidate for grade_candidate.py.
This intentionally ignores inclusion handling to test the grader's strictness.
"""


def solve(bars):
    tops = []
    bottoms = []
    for i in range(1, len(bars) - 1):
        if bars[i].high > bars[i - 1].high and bars[i].high > bars[i + 1].high:
            tops.append(i)
        if bars[i].low < bars[i - 1].low and bars[i].low < bars[i + 1].low:
            bottoms.append(i)

    return {
        "fractals": {"tops": tops, "bottoms": bottoms, "index_space": "original"},
        "pens": [],
        "pens_index_space": "original",
    }
