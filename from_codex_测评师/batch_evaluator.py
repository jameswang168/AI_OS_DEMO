import json
import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CANDIDATE_DIR = BASE_DIR / "candidates"
ANSWERS_FILE = BASE_DIR / "standard_answers.json"
REPORT_FILE = BASE_DIR / "leaderboard.json"
GRADER = BASE_DIR / "grade_candidate.py"


def _run_candidate(path: Path) -> dict:
    cmd = [
        "python",
        str(GRADER),
        "--candidate",
        str(path),
        "--answers",
        str(ANSWERS_FILE),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    stdout = proc.stdout.strip()
    if not stdout:
        return {"candidate_name": path.name, "error": "NoOutput"}
    try:
        payload = json.loads(stdout.splitlines()[-1])
        payload["candidate_name"] = path.name
        return payload
    except json.JSONDecodeError:
        return {"candidate_name": path.name, "error": "InvalidJSON", "raw": stdout[-500:]}


def run_batch() -> None:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    if not ANSWERS_FILE.exists():
        print(f"Missing standard answers: {ANSWERS_FILE}")
        return
    if not GRADER.exists():
        print(f"Missing grader: {GRADER}")
        return

    results = []
    for file in sorted(CANDIDATE_DIR.glob("*.py")):
        print(f"Evaluating: {file.name}")
        results.append(_run_candidate(file))

    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Leaderboard written to: {REPORT_FILE}")


if __name__ == "__main__":
    run_batch()
