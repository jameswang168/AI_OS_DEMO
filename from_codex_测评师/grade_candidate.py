from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import time
from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Optional, Tuple

from scoring_protocol import compute_total_score


@dataclass(frozen=True)
class Bar:
    open: float
    high: float
    low: float
    close: float


def _load_candidate_module(path: str):
    spec = importlib.util.spec_from_file_location("candidate_module", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load candidate module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bars_from_json(bars_json: List[Dict[str, Any]]) -> List[Bar]:
    return [Bar(**item) for item in bars_json]


def _normalize_fractal_output(
    output: Dict[str, Any]
) -> Tuple[List[int], List[int], str]:
    """
    Normalize fractal output to (tops, bottoms, index_space).
    index_space: "merged" or "original"
    """
    fractals = output.get("fractals", output)
    tops = fractals.get("tops", fractals.get("tops_merged", []))
    bottoms = fractals.get("bottoms", fractals.get("bottoms_merged", []))
    index_space = fractals.get("index_space", "merged")
    return list(tops), list(bottoms), index_space


def _normalize_pen_output(output: Dict[str, Any]) -> Tuple[List[List[Any]], str]:
    pens = output.get("pens", output.get("pens_merged", []))
    index_space = output.get("pens_index_space", output.get("index_space", "merged"))
    normalized = [list(pen) for pen in pens]
    return normalized, index_space


def _compare_list(a: List[Any], b: List[Any]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return 1.0 if a == b else 0.0


def _run_candidate(
    candidate_path: str,
    bars_json: List[Dict[str, Any]],
    queue: Queue,
) -> None:
    try:
        module = _load_candidate_module(candidate_path)
        bars = _bars_from_json(bars_json)

        if hasattr(module, "solve"):
            result = module.solve(bars)
        else:
            # Optional procedural API
            if not hasattr(module, "merge_inclusions") or not hasattr(module, "detect_fractals"):
                raise AttributeError("Candidate must provide solve() or merge_inclusions() + detect_fractals().")
            merged, groups = module.merge_inclusions(bars)
            tops, bottoms = module.detect_fractals(merged)
            pens = []
            if hasattr(module, "build_pens"):
                pens = module.build_pens(tops, bottoms, min_gap=1)
            result = {
                "fractals": {"tops": tops, "bottoms": bottoms, "index_space": "merged"},
                "pens": pens,
                "pens_index_space": "merged",
                "groups": groups,
            }

        queue.put({"ok": True, "result": result})
    except MemoryError:
        queue.put({"ok": False, "error": "MemoryError"})
    except Exception as exc:  # noqa: BLE001
        queue.put({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


def _eval_case(
    candidate_path: str,
    bars_json: List[Dict[str, Any]],
    answer: Dict[str, Any],
    timeout_seconds: float,
) -> Dict[str, Any]:
    queue: Queue = Queue()
    process = Process(target=_run_candidate, args=(candidate_path, bars_json, queue))
    start = time.perf_counter()
    process.start()
    process.join(timeout_seconds)

    runtime = time.perf_counter() - start
    if process.is_alive():
        process.terminate()
        process.join()
        return {"ok": False, "error": "Timeout", "runtime": runtime}

    if queue.empty():
        return {"ok": False, "error": "NoResult", "runtime": runtime}

    payload = queue.get()
    if not payload.get("ok"):
        return {"ok": False, "error": payload.get("error", "Unknown"), "runtime": runtime}

    result = payload["result"]
    tops, bottoms, index_space = _normalize_fractal_output(result)
    pens, pens_index_space = _normalize_pen_output(result)

    expected = answer["answer"]
    tops_expected_merged = expected["fractals"]["tops_merged"]
    bottoms_expected_merged = expected["fractals"]["bottoms_merged"]
    tops_expected_original = expected["fractals"]["tops_original"]
    bottoms_expected_original = expected["fractals"]["bottoms_original"]

    if index_space == "original":
        fractal_score = 0.5 * _compare_list(tops, tops_expected_original) + 0.5 * _compare_list(
            bottoms, bottoms_expected_original
        )
    else:
        fractal_score = 0.5 * _compare_list(tops, tops_expected_merged) + 0.5 * _compare_list(
            bottoms, bottoms_expected_merged
        )

    pens_expected = expected["pens_merged"]
    if pens_index_space != "merged":
        pen_score = 0.0
    else:
        pen_score = _compare_list(pens, pens_expected)

    return {
        "ok": True,
        "runtime": runtime,
        "fractal_score": fractal_score,
        "pen_score": pen_score,
        "index_space": index_space,
        "pens_index_space": pens_index_space,
    }


def _cost_efficiency_score(runtime: float, limit_seconds: float) -> float:
    if runtime <= 0:
        return 0.0
    ratio = runtime / limit_seconds
    return max(0.0, min(1.0, 1.0 - ratio))


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade candidate code against standard answers.")
    parser.add_argument("--candidate", required=True, help="Path to candidate .py file")
    parser.add_argument(
        "--answers",
        default="standard_answers.json",
        help="Path to standard_answers.json",
    )
    parser.add_argument("--timeout", type=float, default=2.0, help="Timeout per case (seconds)")
    parser.add_argument("--runtime_limit", type=float, default=1.0, help="Runtime limit for cost score")
    args = parser.parse_args()

    if not os.path.exists(args.candidate):
        raise FileNotFoundError(args.candidate)
    if not os.path.exists(args.answers):
        raise FileNotFoundError(args.answers)

    with open(args.answers, "r", encoding="utf-8") as f:
        answers = json.load(f)

    case_results = {}
    runtimes = []
    fractal_scores = []
    pen_scores = []
    errors = []

    for case_name, payload in answers.items():
        bars_json = payload["bars"]
        result = _eval_case(
            candidate_path=args.candidate,
            bars_json=bars_json,
            answer=payload,
            timeout_seconds=args.timeout,
        )
        case_results[case_name] = result
        if result["ok"]:
            runtimes.append(result["runtime"])
            fractal_scores.append(result["fractal_score"])
            pen_scores.append(result["pen_score"])
        else:
            errors.append({"case": case_name, "error": result.get("error")})

    avg_fractal = sum(fractal_scores) / len(fractal_scores) if fractal_scores else 0.0
    avg_pen = sum(pen_scores) / len(pen_scores) if pen_scores else 0.0
    avg_runtime = sum(runtimes) / len(runtimes) if runtimes else math.inf

    code_execution = max(0.0, min(1.0, 0.6 * avg_fractal + 0.4 * avg_pen))
    logic_consistency = case_results.get("inclusion", {}).get("fractal_score", 0.0)
    cost_efficiency = _cost_efficiency_score(avg_runtime, args.runtime_limit)
    chan_theory = avg_pen

    scores = {
        "code_execution": code_execution,
        "logic_consistency": logic_consistency,
        "completion": 1.0 if not errors else max(0.0, 1.0 - len(errors) / 3.0),
        "self_consistency": 1.0 if len(set(fractal_scores)) <= 1 else 0.5,
        "stability": 1.0 if avg_runtime < args.runtime_limit else 0.5,
        "cost_efficiency": cost_efficiency,
        "chan_theory": chan_theory,
        "hallucination": 1.0 if errors else 0.0,
    }

    total = compute_total_score(scores)

    report = {
        "scores": scores,
        "total_score": total.total_score,
        "missing_fields": list(total.missing_fields),
        "case_results": case_results,
        "errors": errors,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
