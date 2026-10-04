# Agentic AI Unit-Test Generation Pipeline (CSE731 Mid-term Project)

CSE731 Software Testing, Term I 2026-27, IIIT Bangalore.
**Team:** Undi Trivedh Venkata Sai (IMT2023002), Katakam Shashidhar Sai (IMT2023567)

Testing goal: **Option 1 - achieve a user-specified coverage criterion** (statement or branch/decision coverage).

```
MBPP problem --> [1] Code Generator --> solution.py
                                            |
                 +--------------------------+
                 v
         [2] Test Generator --> test_solution.py --> [3] Test Executor --> verdict
                 ^                                          |  (pytest + coverage.py,
                 +--------- feedback: uncovered lines, -----+   LLM failure triage)
                            untaken branches, wrong tests
                 (loop until target coverage is met or max iterations reached)
```

- **Dataset:** MBPP sanitized (427 hand-verified problems), test split (task ids 11-510). Downloaded automatically to `data/` on first run.
- **LLM:** any OpenAI-compatible endpoint; default OpenRouter free model `google/gemma-4-31b-it:free`.
  Model reasoning/"thinking" is explicitly disabled (`reasoning: {enabled: false}`) because the assignment forbids chain-of-thought.
- **No frameworks:** no LangChain/LangGraph, no RAG. Each agent is one Python class that sends a system + user prompt through `llm_client.py` (plain `requests`).

## Agents

| Agent | File | LLM? | Input -> Output |
|---|---|---|---|
| 1. Code Generator | `agents/code_generator.py` | yes (T=0.2) | problem text + first MBPP assert (fixes the signature) -> Python function. Retries only if the code doesn't parse or lacks the function. |
| 2. Test Generator | `agents/test_generator.py` | yes (T=0.2) | problem + numbered code + coverage criterion (+ previous tests and executor feedback) -> pytest file |
| 3. Test Executor | `agents/test_executor.py` | triage only (T=0.0) | runs pytest with `coverage.py` branch measurement in a sandboxed subprocess, asks the LLM to classify each failing test as a *code* bug or a *test* bug, returns a verdict + feedback |

Verdicts: `PASS`, `COVERAGE_NOT_MET`, `TEST_BUG`, `CODE_BUG_FOUND`, `ERROR`.

**Independent evaluation (not visible to any agent):**
- *Code correctness:* the generated function is run against all MBPP reference asserts.
- *Oracle validity:* the final generated tests are run against the MBPP reference solution; a test that fails there has a wrong expected value.

## Results (final run `runs/branch10_v2`, 10 MBPP problems, 100% branch-coverage target)

| Metric | Value |
|---|---|
| Coverage target met | 10/10 (mean statement and branch coverage 100%) |
| Generated code correct on hidden MBPP asserts | 9/10 |
| Incorrect generated code caught by the generated tests | 1/1 (task 16) |
| Tests whose expected values hold on the MBPP reference solution | 85/86 (98.8%) |
| Mean generate-execute-feedback rounds | 1.4 (max 3) |

`runs/branch10` is the first run, kept to show the issues we found and fixed (a pytest collection bug for
functions named `test_*`, and model replies that were prose instead of code). See `summary.md` in each run.

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env      # then paste your OpenRouter key into .env
```

## Running

```bash
# 10 problems, 100% branch coverage, up to 3 feedback iterations
python pipeline.py --criterion branch --target 100 --limit 10 --run-name branch10

# specific problems, statement coverage
python pipeline.py --tasks 11,12,17 --criterion statement --run-name stmt_demo

# re-running the same --run-name resumes (finished problems are skipped)
# rebuild summary tables only
python pipeline.py --run-name branch10 --summary-only
```

Free OpenRouter models are rate limited (~20 requests/min; the daily cap depends on your account credits).
One problem costs about 2-7 LLM calls. If the daily cap is hit the run stops cleanly and can be resumed.

## Output (`runs/<run-name>/`) -> report sections

| File | Report item |
|---|---|
| `config.json` - model, temperatures, max_tokens, top_p, seed, criterion, target | 2 (settings) |
| `prompts.md` - all system prompts and user-prompt templates | 2 (prompts) |
| `llm_calls.jsonl` - every actual prompt/response with params, tokens, latency | 2, 3 |
| `task_<id>/solution.py`, `task_<id>/final_tests.py` | 3 (code and tests) |
| `task_<id>/iter_<k>/` - tests, pytest output, `coverage.json`, `junit.xml`, `execution_report.json` (verdict + feedback) | 3, 4 |
| `task_<id>/result.json`, `summary.md`, `summary.csv` | 4 (execution results) |

## Files

```
pipeline.py          orchestrator + summary/metrics
config.py            all settings (dumped to config.json)
prompts.py           all prompt templates
llm_client.py        OpenAI-compatible HTTP client, retries, rate limiting, call log
dataset.py           MBPP loader
sandbox.py           isolated pytest + coverage.py runner and result parsing
agents/              the three agents
```
