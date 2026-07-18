"""Prompt evaluation harness for maintenance copilot structured outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.llm.maintenance_copilot import recommend

GOLDEN_SET = Path(__file__).parent / "golden_set.json"


def run_eval(mock: bool = True) -> dict:
    with open(GOLDEN_SET) as f:
        cases = json.load(f)

    passed = 0
    failures: list[str] = []

    for i, case in enumerate(cases):
        loco = case["locomotive_id"]
        use_mock = mock or case.get("mock", True)
        result = recommend(loco, mock=use_mock)

        ok = True
        if "expect_severity_in" in case:
            if result.severity not in case["expect_severity_in"]:
                ok = False
                failures.append(
                    f"Case {i}: {loco} severity {result.severity!r} not in {case['expect_severity_in']}"
                )

        if ok and "expect_action_contains" in case:
            action_lower = result.recommended_action.lower()
            if not any(kw.lower() in action_lower for kw in case["expect_action_contains"]):
                ok = False
                failures.append(
                    f"Case {i}: {loco} action missing expected keywords"
                )

        if ok and "expect_summary_contains" in case:
            summary_lower = result.summary.lower()
            if not any(kw.lower() in summary_lower for kw in case["expect_summary_contains"]):
                ok = False
                failures.append(f"Case {i}: {loco} summary missing expected content")

        if ok:
            passed += 1

    total = len(cases)
    report = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 2) if total else 0.0,
        "failures": failures,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate maintenance copilot outputs")
    parser.add_argument("--mock", action="store_true", default=True, help="Use mock mode (default)")
    parser.add_argument("--live", action="store_true", help="Call Anthropic API (requires ANTHROPIC_API_KEY)")
    args = parser.parse_args()
    mock = not args.live

    report = run_eval(mock=mock)
    print(json.dumps(report, indent=2))

    if report["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
