---
name: maintenance-rag
description: Add a maintenance bulletin to the RAG index and re-run copilot evaluation. Use when extending maintenance knowledge base, bulletins, or fault-code coverage.
---

# Maintenance RAG Skill

## Workflow

1. **Add bulletin** — append a new object to `data/sample/maintenance_bulletins.json`:

```json
{
  "bulletin_id": "MB-2026-0XX",
  "fault_code": "Fxxx",
  "title": "Short title",
  "severity": "high|medium|low",
  "recommended_action": "Operator action text",
  "effective_date": "YYYY-MM-DD"
}
```

2. **Re-run pipelines** so silver layer picks up bulletin joins:

```bash
python -m src.pipelines.run_all
```

3. **Test copilot** for a locomotive with matching fault code:

```bash
python -m src.llm.maintenance_copilot LOC-4401 --mock
```

4. **Update golden set** — add a case to `evals/golden_set.json` if the new bulletin changes expected outputs

5. **Re-run eval**:

```bash
python evals/prompt_eval.py --mock
```

## Production note

In a real deployment, bulletins would be indexed in a vector store (Azure AI Search, Databricks Vector Search) with chunking and metadata filters on `fault_code`. This repo uses JSON + fault-code matching as a local stub.
