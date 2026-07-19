# Demo walkthrough

A **5–10 minute walkthrough** of the repo's domain layer and Claude Code architecture. Assumes you have cloned the repo and activated the virtual environment.

## Before you start

```bash
cd claude-rail-service-analytics
source .venv/bin/activate   # or: python3 -m venv .venv && pip install -e ".[dev]"

python -m src.pipelines.run_all
pytest -q
```

Expected: pipelines complete, tests pass.

---

## Part 1: Domain story (2 min)

**Say:** *"This is a synthetic rail Service Analytics stack. Telematics events flow through medallion layers to KPIs operators care about, then a maintenance copilot turns faults into recommended actions."*

Show the synthetic sources:

```bash
head -5 data/sample/telematics_events.csv
python -c "import json; print(json.dumps(json.load(open('data/sample/maintenance_bulletins.json'))[:2], indent=2))"
```

Show gold output exists:

```bash
python -c "
import pandas as pd
g = pd.read_parquet('data/gold/service_metrics.parquet')
print(g[g['recommended_review']].head())
"
```

**Key point:** Bronze = raw, silver = cleaned + bulletin join, gold = aggregated `recommended_review` flags.

---

## Part 2: Claude Code Skills (1 min)

**Say:** *"Skills are reusable slash-command workflows — I built three that match how this team would actually work."*

Open in editor or list:

- `.claude/skills/databricks-pipeline/SKILL.md` — medallion checklist
- `.claude/skills/prompt-eval/SKILL.md` — eval before shipping prompts
- `.claude/skills/maintenance-rag/SKILL.md` — extend bulletin knowledge base

If Claude Code CLI is available:

```bash
claude
# In session: /prompt-eval
```

Otherwise run the skill's command directly:

```bash
python evals/prompt_eval.py --mock
```

**Key point:** README explains *why* each skill exists, not just that they exist.

---

## Part 3: Sub-agents (1 min)

**Say:** *"Sub-agents are delegated specialists with isolated context — I use them for review, not for deterministic checks."*

Show:

- `.claude/agents/pipeline-reviewer.md` — medallion + idempotency review
- `.claude/agents/prompt-engineer.md` — structured output + eval coverage

If using Claude Code:

```
Use the pipeline-reviewer agent to review src/pipelines/
```

**Key point:** Different tool sets (`pipeline-reviewer` includes Bash; `prompt-engineer` is read-only).

---

## Part 4: Hooks and settings (1 min)

**Say:** *"Hooks enforce must-hold rules every time — blocking secrets and linting Python after edits."*

Show [`.claude/settings.json`](../.claude/settings.json) hook wiring.

Demo block-secrets (safe test input):

```bash
echo '{"tool_name":"Write","tool_input":{"content":"key=sk-ant-test123"}}' \
  | .claude/hooks/block-secrets.sh
```

Expected: JSON with `"permissionDecision": "deny"`.

**Key point:** Hooks are deterministic; Skills are procedural; agents are judgment-heavy.

---

## Part 5: MCP catalog (1 min)

**Say:** *"MCP lets Claude query the data catalog without hallucinating schema — in production this would be Unity Catalog."*

With pipelines already run:

```bash
# If Claude Code is connected, use MCP tools: list_tables, sample_rows
# Or show the server definition:
cat .mcp.json
head -40 catalog_mcp/telematics_catalog/server.py
```

Tools exposed:

| Tool | Purpose |
|------|---------|
| `list_tables` | bronze/silver/gold table names |
| `describe_table` | Column metadata |
| `sample_rows` | Read-only sample from parquet |

**Key point:** Custom MCP server, not just a config pointing at a generic filesystem server.

---

## Part 6: LLM copilot + eval (1 min)

**Say:** *"The copilot returns structured JSON an operator system could consume — and I eval it before shipping prompt changes."*

```bash
python -m src.llm.maintenance_copilot LOC-4406 --mock
python evals/prompt_eval.py --mock
```

Show `src/llm/schemas.py` — `OperatorRecommendation` Pydantic model.

**Key point:** Mock mode works without an API key — clone, run pipelines, and verify the copilot locally.

---

## Part 7: Close — production mapping (30 sec)

**Say:** *"This stops at local Python, but the patterns map directly: Delta jobs for pipelines, Vector Search for bulletins, Unity Catalog MCP, CI eval for prompts, and shared `.claude/` config for the team's Claude Code hygiene."*

Refer to [ARCHITECTURE.md](../ARCHITECTURE.md) production mapping table.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP `sample_rows` fails | Run `python -m src.pipelines.run_all` first |
| Eval fails | Ensure gold/silver parquet exists; run pipelines |
| Import errors | `pip install -e ".[dev]"` from repo root |
| Claude Code MCP pending | Trust workspace; approve `.mcp.json` server in Claude Code |

---

## Optional: live API demo

Only if you have an Anthropic key and want to show live inference:

```bash
export ANTHROPIC_API_KEY=your-key
python -m src.llm.maintenance_copilot LOC-4406
python evals/prompt_eval.py --live
```

Do not share your screen with the key visible.
