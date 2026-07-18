# Data

All datasets in this repository are **synthetic** and fictional. They are designed to
demonstrate rail service analytics patterns (telematics, maintenance bulletins, KPIs)
for a portfolio project—not real railroad operations data.

## Layout

| Path | Description |
|------|-------------|
| `sample/telematics_events.csv` | Raw locomotive telematics events (committed) |
| `sample/maintenance_bulletins.json` | Maintenance bulletins keyed by fault code (committed) |
| `bronze/` | Generated bronze layer parquet (gitignored) |
| `silver/` | Generated silver layer parquet (gitignored) |
| `gold/` | Generated gold layer KPI parquet (gitignored) |

Generate pipeline outputs:

```bash
uv run python -m src.pipelines.run_all
```
