from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Bar:
    open: float
    high: float
    low: float
    close: float


def _is_inclusion(a: Bar, b: Bar) -> bool:
    return b.high >= a.high and b.low <= a.low


def _trend_direction(prev: Bar, curr: Bar) -> str:
    if curr.high > prev.high and curr.low > prev.low:
        return "up"
    if curr.high < prev.high and curr.low < prev.low:
        return "down"
    return "flat"


def merge_inclusions(bars: List[Bar]) -> Tuple[List[Bar], List[List[int]]]:
    """
    Merge inclusion bars based on trend direction inferred from last two non-inclusion bars.
    Strategy:
      - Track last two merged bars to infer trend.
      - If inclusion occurs, keep the more extreme bar based on trend:
        up: keep higher high and higher low
        down: keep lower high and lower low
        flat: keep the newer bar as-is
    Returns merged bars and their original index groups.
    """
    if not bars:
        return [], []

    merged: List[Bar] = []
    groups: List[List[int]] = []
    trend = "flat"

    def update_trend() -> None:
        nonlocal trend
        if len(merged) >= 2:
            trend = _trend_direction(merged[-2], merged[-1])

    for i, bar in enumerate(bars):
        if not merged:
            merged.append(bar)
            groups.append([i])
            continue

        last = merged[-1]
        if _is_inclusion(last, bar) or _is_inclusion(bar, last):
            if trend == "up":
                new_bar = Bar(
                    open=bar.open,
                    high=max(last.high, bar.high),
                    low=max(last.low, bar.low),
                    close=bar.close,
                )
            elif trend == "down":
                new_bar = Bar(
                    open=bar.open,
                    high=min(last.high, bar.high),
                    low=min(last.low, bar.low),
                    close=bar.close,
                )
            else:
                new_bar = bar
            merged[-1] = new_bar
            groups[-1].append(i)
            update_trend()
            continue

        merged.append(bar)
        groups.append([i])
        update_trend()

    return merged, groups


def detect_fractals(bars: List[Bar]) -> Tuple[List[int], List[int]]:
    tops: List[int] = []
    bottoms: List[int] = []
    for i in range(1, len(bars) - 1):
        if bars[i].high > bars[i - 1].high and bars[i].high > bars[i + 1].high:
            tops.append(i)
        if bars[i].low < bars[i - 1].low and bars[i].low < bars[i + 1].low:
            bottoms.append(i)
    return tops, bottoms


def build_pens(
    tops: List[int],
    bottoms: List[int],
    min_gap: int = 1,
) -> List[Tuple[int, int, str]]:
    """
    Build pens from alternating tops/bottoms.
    min_gap: number of independent bars required between fractals.
    """
    marks = [(i, "top") for i in tops] + [(i, "bottom") for i in bottoms]
    marks.sort(key=lambda x: x[0])
    pens: List[Tuple[int, int, str]] = []
    for i in range(1, len(marks)):
        prev_idx, prev_type = marks[i - 1]
        curr_idx, curr_type = marks[i]
        if curr_type == prev_type:
            continue
        if curr_idx - prev_idx <= min_gap:
            continue
        direction = "up" if prev_type == "bottom" and curr_type == "top" else "down"
        pens.append((prev_idx, curr_idx, direction))
    return pens


def map_fractals_to_original(
    fractals: List[int],
    groups: List[List[int]],
    prefer: str = "last",
) -> List[int]:
    mapped: List[int] = []
    for idx in fractals:
        group = groups[idx]
        mapped.append(group[-1] if prefer == "last" else group[0])
    return mapped


def dataset_standard() -> List[Bar]:
    return [
        Bar(10, 12, 9, 11),
        Bar(11, 13, 10, 12),
        Bar(12, 11, 8, 9),
        Bar(9, 10, 7, 8),
        Bar(8, 14, 8, 13),
        Bar(13, 12, 9, 10),
        Bar(10, 15, 10, 14),
        Bar(14, 13, 11, 12),
        Bar(12, 16, 11, 15),
        Bar(15, 14, 12, 13),
    ]


def dataset_inclusion() -> List[Bar]:
    return [
        Bar(10, 12, 9, 11),
        Bar(11, 13, 10, 12),
        Bar(12, 14, 8, 9),
        Bar(9, 12, 9, 11),
        Bar(11, 12, 8, 9),
        Bar(9, 15, 9, 14),
        Bar(14, 16, 12, 13),
        Bar(13, 15, 11, 12),
        Bar(12, 14, 10, 11),
        Bar(11, 13, 9, 10),
    ]


def dataset_reversal() -> List[Bar]:
    return [
        Bar(10, 11, 9, 10),
        Bar(10, 12, 9, 11),
        Bar(11, 13, 10, 12),
        Bar(12, 12.5, 9.5, 10),
        Bar(10, 11, 8, 9),
        Bar(9, 10, 7, 8),
        Bar(8, 11, 8, 10),
        Bar(10, 12, 9, 11),
        Bar(11, 12, 10, 11),
        Bar(11, 13, 10, 12),
        Bar(12, 11, 9, 10),
        Bar(10, 9.5, 8, 8.5),
    ]


def generate_answer(bars: List[Bar]) -> Dict[str, object]:
    merged, groups = merge_inclusions(bars)
    tops, bottoms = detect_fractals(merged)
    pens = build_pens(tops, bottoms, min_gap=1)
    return {
        "merged_count": len(merged),
        "fractals": {
            "tops_merged": tops,
            "bottoms_merged": bottoms,
            "tops_original": map_fractals_to_original(tops, groups),
            "bottoms_original": map_fractals_to_original(bottoms, groups),
        },
        "pens_merged": pens,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate standard answers for fractal/pen tasks.")
    parser.add_argument("--output", default="standard_answers.json", help="Output JSON path.")
    args = parser.parse_args()

    datasets = {
        "standard": dataset_standard(),
        "inclusion": dataset_inclusion(),
        "reversal": dataset_reversal(),
    }

    answers = {}
    for name, bars in datasets.items():
        answers[name] = {
            "bars": [bar.__dict__ for bar in bars],
            "answer": generate_answer(bars),
        }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)

    print(f"Wrote standard answers to {args.output}")


if __name__ == "__main__":
    main()
