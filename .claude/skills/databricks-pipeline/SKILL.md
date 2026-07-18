---
name: databricks-pipeline
description: Scaffold or extend bronze, silver, and gold telematics pipelines using medallion architecture. Use when adding pipeline code, Databricks jobs, or PySpark transforms for telematics data.
---

# Databricks Pipeline Skill

## Context

This repo uses a **local medallion mock** of a Databricks deployment:

| Layer | Module | Output |
|-------|--------|--------|
| Bronze | `src/pipelines/bronze_ingest.py` | `data/bronze/telematics_events.parquet` |
| Silver | `src/pipelines/silver_transform.py` | `data/silver/locomotive_events.parquet` |
| Gold | `src/pipelines/gold_service_metrics.py` | `data/gold/service_metrics.parquet` |

In production these would be Databricks Jobs writing to Delta Lake on ADLS.

## Checklist for new pipeline code

1. Keep layer boundaries strict — bronze is raw+metadata, silver is cleaned/enriched, gold is aggregated KPIs
2. Add `_ingested_at` / `_source_file` metadata in bronze only
3. Make silver transforms **idempotent** (dedupe on `event_id`)
4. Partition gold by `event_date` and `route_id` in a real Databricks deployment
5. Add or update tests in `tests/test_pipelines.py`
6. Run: `python -m src.pipelines.run_all`

## After changes

Run the full pipeline and confirm gold `recommended_review` flags are sensible:

```bash
python -m src.pipelines.run_all
pytest tests/test_pipelines.py -q
```
