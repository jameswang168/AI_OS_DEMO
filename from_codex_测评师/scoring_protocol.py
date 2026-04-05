from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple

DEFAULT_WEIGHTS: Dict[str, float] = {
    "code_execution": 0.35,
    "logic_consistency": 0.25,
    "completion": 0.15,
    "self_consistency": 0.10,
    "stability": 0.10,
    "cost_efficiency": 0.05,
    "chan_theory": 0.10,
    "hallucination": 0.10,
}

SCORE_FIELDS: Tuple[str, ...] = (
    "code_execution",
    "logic_consistency",
    "completion",
    "self_consistency",
    "stability",
    "cost_efficiency",
    "chan_theory",
    "hallucination",
)


@dataclass(frozen=True)
class ScoreResult:
    total_score: float
    normalized_scores: Dict[str, float]
    missing_fields: Tuple[str, ...]
    weights: Dict[str, float]


def _clamp01(value: Optional[float]) -> float:
    if value is None:
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def compute_total_score(
    scores: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> ScoreResult:
    """
    Compute total score using weighted sum.

    Hallucination is a penalty term: total -= weight * hallucination.
    All scores are clamped to [0, 1]. Missing fields default to 0.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    else:
        weights = {**DEFAULT_WEIGHTS, **weights}

    missing = []
    normalized: Dict[str, float] = {}
    for key in SCORE_FIELDS:
        if key not in scores:
            missing.append(key)
        normalized[key] = _clamp01(scores.get(key))

    total = 0.0
    for key, weight in weights.items():
        if key == "hallucination":
            total -= weight * normalized.get(key, 0.0)
        else:
            total += weight * normalized.get(key, 0.0)

    return ScoreResult(
        total_score=_clamp01(total),
        normalized_scores=normalized,
        missing_fields=tuple(missing),
        weights=weights,
    )


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        # Accept "YYYY-MM-DD HH:MM:SS" or ISO strings
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def validate_timestamps(
    data_timestamp: Any,
    inference_timestamp: Any,
    max_delay_seconds: int = 60,
) -> Dict[str, Any]:
    """
    Validate timestamp ordering and delay.

    Returns:
      ok: bool
      delay_seconds: Optional[float]
      flags: list of strings
    """
    flags = []
    data_ts = _parse_timestamp(data_timestamp)
    infer_ts = _parse_timestamp(inference_timestamp)
    if data_ts is None or infer_ts is None:
        flags.append("timestamp_parse_failed")
        return {"ok": False, "delay_seconds": None, "flags": flags}

    delay = (infer_ts - data_ts).total_seconds()
    if delay < 0:
        flags.append("inference_before_data")
    if delay > max_delay_seconds:
        flags.append("inference_delay_exceeds_limit")

    return {
        "ok": len(flags) == 0,
        "delay_seconds": delay,
        "flags": flags,
    }


def normalize_scores_in_place(scores: Dict[str, Any]) -> Dict[str, float]:
    """
    Normalize a score dict to [0,1] in-place-friendly way.
    Returns a new dict with normalized values.
    """
    return {key: _clamp01(scores.get(key)) for key in SCORE_FIELDS}


def score_from_log_entry(
    log_entry: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> ScoreResult:
    """
    Convenience wrapper to compute total score from a log entry that
    contains a 'scores' object.
    """
    scores = log_entry.get("scores", {})
    return compute_total_score(scores, weights=weights)
