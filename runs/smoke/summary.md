# Run `smoke`

- Model: `google/gemma-4-31b-it:free` (fallbacks: google/gemma-4-26b-a4b-it:free, nvidia/nemotron-3-super-120b-a12b:free) | criterion: **branch** | target: **100%** | max iterations: 3
- Temperatures: code 0.2, tests 0.2, triage 0.0 | top_p 1.0 | seed 42 | reasoning disabled: True

## Aggregate metrics

| Metric | Value |
|---|---|
| Problems | 1 |
| Generated code correct (all MBPP reference tests pass) | 1/1 |
| Coverage target met | 1/1 |
| Mean statement coverage (final) | 100.0% |
| Mean branch coverage (final) | 100.0% |
| Mean branch coverage, iteration 1 -> final | 100.0% -> 100.0% |
| Mean iterations used | 1.00 |
| Tests generated (final suites) | 8 |
| Test-oracle validity (tests passing on MBPP reference solution) | 8/8 (100.0%) |
| Incorrect generated code caught by the generated tests | 0/0 |
| Verdicts | PASS: 1 |
| LLM calls / total tokens | 2 / 943 |
| Models that answered (calls) | `nvidia/nemotron-3-super-120b-a12b:free` (2) |

## Per-problem results

| Task | Function | Code correct | Iter. | Tests (pass/total) | Stmt % | Branch % | Target met | Verdict | Oracle valid | Coverage by iteration |
|---|---|---|---|---|---|---|---|---|---|---|
| 11 | `remove_Occ` | yes (3/3) | 1 | 8/8 | 100 | 100 | yes | PASS | 8/8 | 100 |
