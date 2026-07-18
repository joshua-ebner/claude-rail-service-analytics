"""Silver layer: clean, enrich, and join maintenance bulletin metadata."""

import json

import pandas as pd

from src.pipelines.paths import (
    BRONZE_TELEMATICS,
    BULLETINS_JSON,
    SILVER_LOCOMOTIVE_EVENTS,
    ensure_layer_dirs,
)


def _load_bulletins(path: str | None = None) -> pd.DataFrame:
    bulletins_path = path or str(BULLETINS_JSON)
    with open(bulletins_path) as f:
        records = json.load(f)
    return pd.DataFrame(records)


def run(
    bronze_path: str | None = None,
    bulletins_path: str | None = None,
    output_path: str | None = None,
) -> pd.DataFrame:
    """Transform bronze telematics and attach bulletin severity when fault codes match."""
    ensure_layer_dirs()
    bronze_file = bronze_path or str(BRONZE_TELEMATICS)
    out_path = output_path or str(SILVER_LOCOMOTIVE_EVENTS)

    df = pd.read_parquet(bronze_file)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df["event_date"] = df["timestamp_utc"].dt.date.astype(str)
    df["has_fault"] = df["fault_code"].astype(str).str.len() > 0

    # Normalize fault codes for joins
    df["fault_code_norm"] = df["fault_code"].replace("", pd.NA)

    bulletins = _load_bulletins(bulletins_path)
    bulletin_lookup = bulletins.drop_duplicates(subset=["fault_code"], keep="first")

    df = df.merge(
        bulletin_lookup[["fault_code", "severity", "recommended_action", "title"]],
        left_on="fault_code_norm",
        right_on="fault_code",
        how="left",
        suffixes=("", "_bulletin"),
    )
    df = df.drop(columns=["fault_code_bulletin", "fault_code_norm"], errors="ignore")
    df["severity"] = df["severity"].fillna("none")
    df["recommended_action"] = df["recommended_action"].fillna("")

    # Deduplicate on event_id (idempotent silver transform)
    df = df.drop_duplicates(subset=["event_id"], keep="last")

    df.to_parquet(out_path, index=False)
    return df
