# Run `branch10_v2`

- Model: `google/gemma-4-31b-it:free` (fallbacks: google/gemma-4-26b-a4b-it:free, nvidia/nemotron-3-super-120b-a12b:free) | criterion: **branch** | target: **100%** | max iterations: 3
- Temperatures: code 0.2, tests 0.2, triage 0.0 | top_p 1.0 | seed 42 | reasoning disabled: True

## Aggregate metrics

| Metric | Value |
|---|---|
| Problems | 10 |
| Generated code correct (all MBPP reference tests pass) | 9/10 |
| Coverage target met | 10/10 |
| Mean statement coverage (final) | 100.0% |
| Mean branch coverage (final) | 100.0% |
| Mean branch coverage, iteration 1 -> final | 100.0% -> 100.0% |
| Mean iterations used | 1.40 |
| Tests generated (final suites) | 86 |
| Test-oracle validity (tests passing on MBPP reference solution) | 85/86 (98.8%) |
| Incorrect generated code caught by the generated tests | 1/1 |
| Verdicts | CODE_BUG_FOUND: 1, PASS: 9 |
| Unusable test-generator replies re-requested (prose / truncated) | 0 |
| LLM calls / total tokens | 30 / 17397 |
| Models that answered (calls) | `nvidia/nemotron-3-super-120b-a12b:free` (27), `google/gemma-4-26b-a4b-it:free` (1), `google/gemma-4-31b-it:free` (1) |

## Per-problem results

| Task | Function | Code correct | Iter. | Tests (pass/total) | Stmt % | Branch % | Target met | Verdict | Oracle valid | Coverage by iteration |
|---|---|---|---|---|---|---|---|---|---|---|
| 11 | `remove_Occ` | yes (3/3) | 1 | 9/9 | 100 | 100 | yes | PASS | 9/9 | 100 |
| 12 | `sort_matrix` | yes (3/3) | 1 | 6/6 | 100 | 100 | yes | PASS | 6/6 | 100 |
| 14 | `find_Volume` | yes (3/3) | 2 | 10/10 | 100 | 100 | yes | PASS | 10/10 | 100 -> 100 |
| 16 | `text_lowercase_underscore` | no (2/3) | 1 | 9/10 | 100 | 100 | yes | CODE_BUG_FOUND | 9/10 | 100 |
| 17 | `square_perimeter` | yes (3/3) | 1 | 4/4 | 100 | 100 | yes | PASS | 4/4 | 100 |
| 18 | `remove_dirty_chars` | yes (3/3) | 3 | 8/8 | 100 | 100 | yes | PASS | 8/8 | 100 -> 100 -> 100 |
| 19 | `test_duplicate` | yes (3/3) | 1 | 5/5 | 100 | 100 | yes | PASS | 5/5 | 100 |
| 20 | `is_woodall` | yes (3/3) | 1 | 16/16 | 100 | 100 | yes | PASS | 16/16 | 100 |
| 56 | `check` | yes (3/3) | 2 | 10/10 | 100 | 100 | yes | PASS | 10/10 | 100 -> 100 |
| 57 | `find_Max_Num` | yes (3/3) | 1 | 8/8 | 100 | 100 | yes | PASS | 8/8 | 100 |
