"""Tests for medallion-style pipeline transforms."""

from pathlib import Path

import pandas as pd
import pytest

from src.pipelines import bronze_ingest, gold_service_metrics, silver_transform
from src.pipelines.paths import BULLETINS_JSON, TELEMATICS_CSV


@pytest.fixture
def temp_data_dirs(tmp_path: Path) -> dict[str, Path]:
    bronze = tmp_path / "bronze" / "telematics_events.parquet"
    silver = tmp_path / "silver" / "locomotive_events.parquet"
    gold = tmp_path / "gold" / "service_metrics.parquet"
    bronze.parent.mkdir(parents=True)
    silver.parent.mkdir(parents=True)
    gold.parent.mkdir(parents=True)
    return {"bronze": bronze, "silver": silver, "gold": gold}


def test_full_pipeline_produces_gold_metrics(temp_data_dirs: dict[str, Path]) -> None:
    bronze_df = bronze_ingest.run(
        source_csv=str(TELEMATICS_CSV),
        output_path=str(temp_data_dirs["bronze"]),
    )
    assert len(bronze_df) > 0
    assert "_ingested_at" in bronze_df.columns

    silver_df = silver_transform.run(
        bronze_path=str(temp_data_dirs["bronze"]),
        bulletins_path=str(BULLETINS_JSON),
        output_path=str(temp_data_dirs["silver"]),
    )
    assert len(silver_df) > 0
    assert "severity" in silver_df.columns
    assert silver_df["event_id"].is_unique

    gold_df = gold_service_metrics.run(
        silver_path=str(temp_data_dirs["silver"]),
        output_path=str(temp_data_dirs["gold"]),
    )
    assert len(gold_df) > 0
    assert "recommended_review" in gold_df.columns
    assert "fault_event_count" in gold_df.columns

    fault_rows = silver_df[silver_df["has_fault"]]
    if len(fault_rows) > 0:
        assert gold_df["fault_event_count"].sum() > 0


def test_bulletin_join_assigns_severity(temp_data_dirs: dict[str, Path]) -> None:
    bronze_ingest.run(
        source_csv=str(TELEMATICS_CSV),
        output_path=str(temp_data_dirs["bronze"]),
    )
    silver_df = silver_transform.run(
        bronze_path=str(temp_data_dirs["bronze"]),
        bulletins_path=str(BULLETINS_JSON),
        output_path=str(temp_data_dirs["silver"]),
    )
    matched = silver_df[silver_df["fault_code"].isin(["F012", "F034", "F078"])]
    assert matched["severity"].isin(["high", "medium", "low"]).any()
