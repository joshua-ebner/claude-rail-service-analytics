"""Maintenance copilot — recommends operator actions from telematics and bulletins."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd

from src.llm.schemas import OperatorRecommendation
from src.pipelines.paths import BULLETINS_JSON, GOLD_SERVICE_METRICS, SILVER_LOCOMOTIVE_EVENTS

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_bulletins() -> list[dict]:
    with open(BULLETINS_JSON) as f:
        return json.load(f)


def lookup_locomotive_history(locomotive_id: str) -> dict:
    """Tool: fetch recent metrics and fault events for a locomotive."""
    result: dict = {"locomotive_id": locomotive_id, "gold_metrics": [], "recent_faults": []}

    if GOLD_SERVICE_METRICS.exists():
        gold = pd.read_parquet(GOLD_SERVICE_METRICS)
        loco_gold = gold[gold["locomotive_id"] == locomotive_id]
        result["gold_metrics"] = loco_gold.head(5).to_dict(orient="records")

    if SILVER_LOCOMOTIVE_EVENTS.exists():
        silver = pd.read_parquet(SILVER_LOCOMOTIVE_EVENTS)
        faults = silver[(silver["locomotive_id"] == locomotive_id) & (silver["has_fault"])]
        result["recent_faults"] = faults.head(5)[
            ["event_id", "fault_code", "severity", "recommended_action", "timestamp_utc"]
        ].to_dict(orient="records")

    return result


def _mock_recommendation(locomotive_id: str) -> OperatorRecommendation:
    history = lookup_locomotive_history(locomotive_id)
    faults = history.get("recent_faults", [])
    if faults:
        top = faults[0]
        return OperatorRecommendation(
            locomotive_id=locomotive_id,
            severity=top.get("severity") or "medium",
            summary=f"Locomotive {locomotive_id} reported fault {top.get('fault_code')} in recent telematics.",
            recommended_action=top.get("recommended_action") or "Review fault logs and contact maintenance.",
            confidence=0.85,
        )
    return OperatorRecommendation(
        locomotive_id=locomotive_id,
        severity="low",
        summary=f"No active faults detected for {locomotive_id} in recent telematics window.",
        recommended_action="Continue normal operations; monitor dashboard KPIs.",
        confidence=0.75,
    )


def _live_recommendation(locomotive_id: str) -> OperatorRecommendation:
    import anthropic

    history = lookup_locomotive_history(locomotive_id)
    bulletins = [b for b in load_bulletins() if any(
        f.get("fault_code") == b["fault_code"] for f in history.get("recent_faults", [])
    )]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""You are a rail maintenance copilot for operators.

Locomotive: {locomotive_id}
Recent metrics: {json.dumps(history.get('gold_metrics', [])[:3])}
Recent faults: {json.dumps(history.get('recent_faults', [])[:3])}
Relevant bulletins: {json.dumps(bulletins[:3])}

Respond with a JSON object matching this schema:
{json.dumps(OperatorRecommendation.model_json_schema(), indent=2)}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        # Production: use prompt caching on static bulletin context blocks
    )
    text = response.content[0].text
    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    payload = json.loads(text[start:end])
    return OperatorRecommendation.model_validate(payload)


def recommend(locomotive_id: str, mock: bool = False) -> OperatorRecommendation:
    if mock or not os.environ.get("ANTHROPIC_API_KEY"):
        return _mock_recommendation(locomotive_id)
    return _live_recommendation(locomotive_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Maintenance copilot for locomotive operators")
    parser.add_argument("locomotive_id", help="e.g. LOC-4401")
    parser.add_argument("--mock", action="store_true", help="Use mock response (no API key)")
    args = parser.parse_args()

    result = recommend(args.locomotive_id, mock=args.mock)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
