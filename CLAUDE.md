# Claude Rail Service Analytics

## Project purpose

Claude Code portfolio project illustrating **rail Service Analytics** patterns: telematics medallion pipelines, a maintenance copilot, and Claude Code tooling. All telematics and maintenance data is synthetic.

**Goal:** Turn locomotive telematics into operator decisions via medallion pipelines and a maintenance copilot, accelerated by Claude Code tooling.

## Directory map

| Path | Purpose |
|------|---------|
| `src/pipelines/` | Bronze / silver / gold Python pipelines (local mock of Databricks) |
| `src/llm/` | Maintenance copilot (Anthropic API + mock mode) |
| `evals/` | Prompt evaluation harness + golden set |
| `catalog_mcp/telematics_catalog/` | MCP server for table catalog and sample rows |
| `.claude/skills/` | Slash-command workflows |
| `.claude/agents/` | Sub-agents for pipeline and prompt review |
| `.claude/hooks/` | Secret blocking and Python lint hooks |
| `data/sample/` | Committed synthetic CSV/JSON sources |

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run pipelines (generates data/bronze|silver|gold/)
python -m src.pipelines.run_all

# Tests
pytest -q

# Copilot (mock — no API key)
python -m src.llm.maintenance_copilot LOC-4406 --mock

# Prompt eval
python evals/prompt_eval.py --mock

# MCP server (stdio — used by Claude Code via .mcp.json)
python -m catalog_mcp.telematics_catalog.server
```

## Medallion conventions

- **Bronze:** raw ingest + `_ingested_at`, `_source_file`
- **Silver:** cleaned events + bulletin join on `fault_code`
- **Gold:** KPIs per locomotive/route/date; `recommended_review` flag for operators

## Secrets

Never commit `.env` or `.claude/settings.local.json`. Use `.env.example` and `settings.local.json.example`.

## Production mapping

In a real Databricks/Azure deployment:

- Pipelines become PySpark jobs on Delta tables
- MCP connects to Unity Catalog or Azure SQL metadata
- Copilot uses Vector Search over maintenance bulletins
- Eval harness runs in CI before prompt deployment
