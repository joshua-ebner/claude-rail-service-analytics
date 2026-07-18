"""Gold layer: aggregate service metrics for operator decisioning."""

import pandas as pd

from src.pipelines.paths import GOLD_SERVICE_METRICS, SILVER_LOCOMOTIVE_EVENTS, ensure_layer_dirs


def run(silver_path: str | None = None, output_path: str | None = None) -> pd.DataFrame:
    """Aggregate locomotive/route/day KPIs for service analytics dashboards."""
    ensure_layer_dirs()
    silver_file = silver_path or str(SILVER_LOCOMOTIVE_EVENTS)
    out_path = output_path or str(GOLD_SERVICE_METRICS)

    df = pd.read_parquet(silver_file)

    grouped = (
        df.groupby(["locomotive_id", "route_id", "event_date"], as_index=False)
        .agg(
            event_count=("event_id", "count"),
            fault_event_count=("has_fault", "sum"),
            avg_speed_mph=("speed_mph", "mean"),
            max_speed_mph=("speed_mph", "max"),
        )
        .round({"avg_speed_mph": 2, "max_speed_mph": 2})
    )

    high_severity = (
        df[df["severity"] == "high"]
        .groupby(["locomotive_id", "route_id", "event_date"], as_index=False)
        .agg(high_severity_fault_count=("event_id", "count"))
    )

    gold = grouped.merge(
        high_severity,
        on=["locomotive_id", "route_id", "event_date"],
        how="left",
    )
    gold["high_severity_fault_count"] = gold["high_severity_fault_count"].fillna(0).astype(int)
    gold["high_severity_fault_flag"] = gold["high_severity_fault_count"] > 0
    gold["recommended_review"] = (gold["fault_event_count"] > 0) | gold["high_severity_fault_flag"]

    gold.to_parquet(out_path, index=False)
    return gold
