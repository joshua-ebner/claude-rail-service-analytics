---
name: prompt-eval
description: Run the maintenance copilot prompt evaluation harness and summarize pass rate. Use when testing prompts, before shipping copilot changes, or when the user mentions eval or golden set.
---

# Prompt Eval Skill

## Run evaluation (mock mode — no API key required)

```bash
python evals/prompt_eval.py --mock
```

## Run live evaluation (requires ANTHROPIC_API_KEY)

```bash
export ANTHROPIC_API_KEY=your-key
python evals/prompt_eval.py --live
```

## Golden set

Test cases live in `evals/golden_set.json`. Each case specifies:

- `locomotive_id` — input to the copilot
- `expect_severity_in` — allowed severity values
- `expect_action_contains` — keywords that must appear in `recommended_action`

## Report format

Summarize for the user:

1. Total cases / passed / failed
2. Pass rate percentage
3. List any failure messages
4. Suggest prompt or golden-set fixes for failures

## Cost governance notes

- Prefer `--mock` during iterative development
- In production, cache static bulletin context blocks in the Anthropic API call
- Route simple lookups to the `lookup_locomotive_history` tool instead of expanding prompts
