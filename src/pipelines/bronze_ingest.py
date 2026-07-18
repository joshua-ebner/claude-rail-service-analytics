"""Bronze layer: ingest raw telematics CSV to parquet.

In production this would be a Databricks Auto Loader or batch job reading from ADLS.
"""

from datetime import datetime, timezone

import pandas as pd

from src.pipelines.paths import BRONZE_TELEMATICS, TELEMATICS_CSV, ensure_layer_dirs


def run(source_csv: str | None = None, output_path: str | None = None) -> pd.DataFrame:
    """Ingest telematics CSV into bronze parquet with ingest metadata."""
    ensure_layer_dirs()
    csv_path = source_csv or str(TELEMATICS_CSV)
    out_path = output_path or str(BRONZE_TELEMATICS)

    df = pd.read_csv(csv_path)
    df["fuel_rate_lph"] = pd.to_numeric(df["fuel_rate_lph"], errors="coerce")
    df["fault_code"] = df["fault_code"].fillna("").astype(str).str.strip()
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df["_source_file"] = csv_path

    df.to_parquet(out_path, index=False)
    return df
