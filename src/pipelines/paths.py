"""Shared paths and helpers for medallion-style pipelines."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

TELEMATICS_CSV = SAMPLE_DIR / "telematics_events.csv"
BULLETINS_JSON = SAMPLE_DIR / "maintenance_bulletins.json"

BRONZE_TELEMATICS = BRONZE_DIR / "telematics_events.parquet"
SILVER_LOCOMOTIVE_EVENTS = SILVER_DIR / "locomotive_events.parquet"
GOLD_SERVICE_METRICS = GOLD_DIR / "service_metrics.parquet"


def ensure_layer_dirs() -> None:
    for directory in (BRONZE_DIR, SILVER_DIR, GOLD_DIR):
        directory.mkdir(parents=True, exist_ok=True)
