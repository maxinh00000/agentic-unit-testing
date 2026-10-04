"""Agentic AI unit-testing pipeline (CSE731 mid-term project).

    MBPP problem --> [1] Code Generator --> code
                                             |
                     +-----------------------+
                     v
             [2] Test Generator --> pytest suite --> [3] Test Executor --> verdict
                     ^                                       |
                     +------- feedback (uncovered lines/ ----+   (repeat until the coverage
                              branches, wrong tests)              target is met or max iterations)

Evaluation only (not seen by any agent): the MBPP reference tests check whether the
generated code is correct, and the MBPP reference solution checks whether the
generated tests' expected values (test oracles) are correct.

Usage:
    python pipeline.py --criterion branch --target 100 --limit 10
    python pipeline.py --tasks 11,12,17 --criterion statement --run-name demo
    python pipeline.py --run-name demo --summary-only
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import prompts
from agents import CodeGeneratorAgent, TestExecutorAgent, TestGeneratorAgent
from config import CRITERIA, RUNS_DIR, Settings, api_key
from dataset import Task, load_mbpp, select_tasks
from llm_client import DailyLimitError, LLMClient
from sandbox import reference_test_file, run_pytest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Agentic AI unit-test generation pipeline (coverage goal)")
    p.add_argument("--criterion", choices=CRITERIA, help="coverage criterion the tests must satisfy")
    p.add_argument("--target", type=float, help="target coverage percentage (default 100)")
    p.add_argument("--max-iters", type=int, help="max generate/execute/feedback rounds per problem")
    p.add_argument("--tasks", help="comma-separated MBPP task ids, e.g. 11,12,17")
    p.add_argument("--start", type=int, default=0, help="offset into the split (ignored with --tasks)")
    p.add_argument("--limit", type=int, default=10, help="number of problems (ignored with --tasks)")
    p.add_argument("--split", choices=["prompt", "test", "validation", "train"], help="MBPP split")
    p.add_argument("--model", help="model id, e.g. google/gemma-4-31b-it:free")
    p.add_argument("--fallback", help="comma-separated fallback model ids, or 'none' to use only --model")
    p.add_argument("--run-name", help="output folder under runs/ (re-using a name resumes that run)")
    p.add_argument("--summary-only", action="store_true", help="only rebuild summary for --run-name")
    return p.parse_args()


# ============================================================================ per-problem flow
def process_task(task: Task, s: Settings, code_agent: CodeGeneratorAgent, test_agent: TestGeneratorAgent,
                 exec_agent: TestExecutorAgent, task_dir: Path) -> dict:
    task_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()

    # ---- Agent 1: code generation
    print(f"  [CodeGen]  generating `{task.entry_point}` ...")
    cg = code_agent.generate(task)
    (task_dir / "solution.py").write_text(cg.code, encoding="utf-8")

    # ---- evaluation: is the generated code correct w.r.t. MBPP's hidden reference tests?
    ref = run_pytest(task_dir / "reference_check", cg.code,
                     reference_test_file(task.test_list, task.test_imports), with_coverage=False,
                     timeout=s.pytest_timeout_s)
    code_correct = ref["total"] > 0 and ref["passed"] == ref["total"]
    print(f"  [CodeGen]  done in {cg.attempts} attempt(s); MBPP reference tests "
          f"{ref['passed']}/{len(task.test_list)} -> code {'CORRECT' if code_correct else 'INCORRECT'}")

    # ---- Agents 2 + 3: generate tests, execute, feed back
    history, prev_tests, feedback = [], None, None
    for it in range(1, s.max_test_iterations + 1):
        print(f"  [TestGen]  iteration {it}: generating tests for {s.criterion} coverage ...")
        tests = test_agent.generate(task, cg.code, prev_tests, feedback)
        report = exec_agent.execute(task, cg.code, tests, task_dir / f"iter_{it}")
        cov = report.get("coverage") or {}
        print(f"  [Executor] iteration {it}: {report['passed']}/{report['total']} passed | "
              f"stmt {cov.get('statement_pct', 0):g}% | branch {cov.get('branch_pct', 0):g}% | "
              f"verdict {report['verdict']}")
        for t in report["triage"]:
            print(f"             - {t['test']}: fault={t['fault']} ({t['reason']})")
        history.append({"iteration": it, "tests": tests, "report": report,
                        "test_gen_attempts": test_agent.last_attempts})
        if not TestExecutorAgent.should_continue(report):
            break
        prev_tests, feedback = tests, report["feedback"]

    best = _choose_best(history)
    final_tests, final = best["tests"], best["report"]
    (task_dir / "final_tests.py").write_text(final_tests, encoding="utf-8")

    # ---- evaluation: are the tests' expected values right? Run them on MBPP's reference solution.
    oracle = run_pytest(task_dir / "oracle_check", task.reference_code, final_tests, with_coverage=False,
                        timeout=s.pytest_timeout_s)
    failing_on_generated = {t["name"] for t in final["tests"] if t["status"] != "passed"}
    passing_on_reference = {t["name"] for t in oracle["tests"] if t["status"] == "passed"}
    real_bug_found = bool(failing_on_generated & passing_on_reference)
    print(f"  [Eval]     final suite (iteration {best['iteration']}) on reference solution: "
          f"{oracle['passed']}/{oracle['total']} tests valid"
          + ("; suite caught a real bug in the generated code" if real_bug_found else ""))

    cov = final.get("coverage") or {}
    return {
        "task_id": task.task_id,
        "function": task.entry_point,
        "prompt": task.prompt,
        "code_attempts": cg.attempts,
        "code_structural_problem": cg.problem,
        "reference_passed": ref["passed"],
        "reference_total": len(task.test_list),
        "code_correct": code_correct,
        "iterations_run": len(history),
        "final_iteration": best["iteration"],
        "tests_total": final["total"],
        "tests_passed": final["passed"],
        "tests_failed": final["failed"],
        "tests_errors": final["errors"],
        "statement_pct": cov.get("statement_pct", 0.0),
        "branch_pct": cov.get("branch_pct", 0.0),
        "statements": cov.get("statements"),
        "branches": cov.get("branches"),
        "criterion_pct": final["criterion_pct"],
        "target_met": final["target_met"],
        "verdict": final["verdict"],
        "verdict_reason": final["verdict_reason"],
        "triage": final["triage"],
        "coverage_by_iteration": [h["report"]["criterion_pct"] for h in history],
        "verdict_by_iteration": [h["report"]["verdict"] for h in history],
        "unusable_test_replies": sum(h["test_gen_attempts"] - 1 for h in history),
        "oracle_valid": oracle["passed"],
        "oracle_total": oracle["total"],
        "real_bug_found": real_bug_found,
        "seconds": round(time.monotonic() - t0, 1),
    }


def _choose_best(history: list[dict]) -> dict:
    """Prefer iterations that meet the target without wrong tests, then higher coverage, then later ones."""
    def key(item):
        idx, h = item
        r = h["report"]
        wrong = sum(t["fault"] != "code" for t in r["triage"])
        clean = r["verdict"] in ("PASS", "CODE_BUG_FOUND")
        return (clean and r["target_met"], r["target_met"], r["verdict"] != "ERROR", -wrong, r["criterion_pct"], idx)
    return max(enumerate(history), key=key)[1]


# ============================================================================ summary
def write_summary(run_dir: Path) -> None:
    results = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(run_dir.glob("task_*/result.json"))]
    results.sort(key=lambda r: r["task_id"])
    if not results:
        print("no results yet")
        return
    cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))

    cols = ["task_id", "function", "code_correct", "reference_passed", "reference_total", "iterations_run",
            "tests_total", "tests_passed", "tests_failed", "statement_pct", "branch_pct", "target_met",
            "verdict", "oracle_valid", "oracle_total", "real_bug_found", "coverage_by_iteration"]
    with (run_dir / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow({**r, "coverage_by_iteration": " -> ".join(f"{c:g}" for c in r["coverage_by_iteration"])})

    n = len(results)
    calls = [json.loads(l) for l in (run_dir / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines() if l]
    tokens = sum(((c.get("usage") or {}).get("total_tokens") or 0) for c in calls)
    models_used: dict[str, int] = {}
    for c in calls:
        if c.get("response"):
            models_used[c["model"]] = models_used.get(c["model"], 0) + 1
    wrong_code = [r for r in results if not r["code_correct"]]
    verdicts = {}
    for r in results:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    oracle_valid, oracle_total = sum(r["oracle_valid"] for r in results), sum(r["oracle_total"] for r in results)

    md = [f"# Run `{run_dir.name}`", "",
          f"- Model: `{cfg['model']}` (fallbacks: {', '.join(cfg.get('fallback_models') or []) or 'none'}) | criterion: **{cfg['criterion']}** | target: **{cfg['target_pct']:g}%** "
          f"| max iterations: {cfg['max_test_iterations']}",
          f"- Temperatures: code {cfg['code_gen']['temperature']}, tests {cfg['test_gen']['temperature']}, "
          f"triage {cfg['triage']['temperature']} | top_p {cfg['top_p']} | seed {cfg['seed']} "
          f"| reasoning disabled: {cfg['disable_reasoning']}",
          "", "## Aggregate metrics", "",
          "| Metric | Value |", "|---|---|",
          f"| Problems | {n} |",
          f"| Generated code correct (all MBPP reference tests pass) | {n - len(wrong_code)}/{n} |",
          f"| Coverage target met | {sum(r['target_met'] for r in results)}/{n} |",
          f"| Mean statement coverage (final) | {mean([r['statement_pct'] for r in results]):.1f}% |",
          f"| Mean branch coverage (final) | {mean([r['branch_pct'] for r in results]):.1f}% |",
          f"| Mean {cfg['criterion']} coverage, iteration 1 -> final | "
          f"{mean([r['coverage_by_iteration'][0] for r in results]):.1f}% -> "
          f"{mean([r['criterion_pct'] for r in results]):.1f}% |",
          f"| Mean iterations used | {mean([r['iterations_run'] for r in results]):.2f} |",
          f"| Tests generated (final suites) | {sum(r['tests_total'] for r in results)} |",
          f"| Test-oracle validity (tests passing on MBPP reference solution) | {oracle_valid}/{oracle_total} "
          f"({100 * oracle_valid / oracle_total if oracle_total else 0:.1f}%) |",
          f"| Incorrect generated code caught by the generated tests | "
          f"{sum(r['real_bug_found'] for r in wrong_code)}/{len(wrong_code)} |",
          f"| Verdicts | {', '.join(f'{k}: {v}' for k, v in sorted(verdicts.items()))} |",
          f"| Unusable test-generator replies re-requested (prose / truncated) | "
          f"{sum(r.get('unusable_test_replies', 0) for r in results)} |",
          f"| LLM calls / total tokens | {len(calls)} / {tokens} |",
          f"| Models that answered (calls) | {', '.join(f'`{m}` ({k})' for m, k in models_used.items())} |",
          "", "## Per-problem results", "",
          "| Task | Function | Code correct | Iter. | Tests (pass/total) | Stmt % | Branch % | "
          "Target met | Verdict | Oracle valid | Coverage by iteration |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        md.append(f"| {r['task_id']} | `{r['function']}` | {'yes' if r['code_correct'] else 'no'} "
                  f"({r['reference_passed']}/{r['reference_total']}) | {r['iterations_run']} | "
                  f"{r['tests_passed']}/{r['tests_total']} | {r['statement_pct']:g} | {r['branch_pct']:g} | "
                  f"{'yes' if r['target_met'] else 'no'} | {r['verdict']} | {r['oracle_valid']}/{r['oracle_total']} | "
                  f"{' -> '.join(f'{c:g}' for c in r['coverage_by_iteration'])} |")
    (run_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nSummary written to {run_dir / 'summary.md'}")
    print("\n".join(md[5:md.index("## Per-problem results")]))


# ============================================================================ main
def main() -> None:
    args = parse_args()
    s = Settings.from_env()
    if args.criterion:
        s.criterion = args.criterion
    if args.target is not None:
        s.target_pct = args.target
    if args.max_iters:
        s.max_test_iterations = args.max_iters
    if args.split:
        s.split = args.split
    if args.model:
        s.model = args.model
    if args.fallback:
        s.fallback_models = [] if args.fallback.lower() == "none" else [m.strip() for m in args.fallback.split(",")]

    run_name = args.run_name or f"{datetime.now():%Y%m%d_%H%M%S}_{s.criterion}"
    run_dir = RUNS_DIR / run_name
    if args.summary_only:
        write_summary(run_dir)
        return

    api_key()  # fail fast before creating any output
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = run_dir / "config.json"
    if cfg_path.exists():  # resuming: keep the settings the run started with
        old = json.loads(cfg_path.read_text(encoding="utf-8"))
        if (old["criterion"], old["target_pct"], old["model"]) != (s.criterion, s.target_pct, s.model):
            sys.exit(f"run '{run_name}' was started with criterion={old['criterion']}, target={old['target_pct']}, "
                     f"model={old['model']}; use a new --run-name for different settings")
    cfg_path.write_text(json.dumps(s.to_dict(), indent=2), encoding="utf-8")
    (run_dir / "prompts.md").write_text(prompts.render_all(s.criterion, s.target_pct), encoding="utf-8")

    ids = [int(x) for x in args.tasks.split(",")] if args.tasks else None
    tasks = select_tasks(load_mbpp(s.split), ids, args.start, args.limit)

    llm = LLMClient(s, run_dir / "llm_calls.jsonl")
    code_agent, test_agent, exec_agent = (CodeGeneratorAgent(llm, s), TestGeneratorAgent(llm, s),
                                          TestExecutorAgent(llm, s))
    print(f"Run '{run_name}': {len(tasks)} MBPP problems | model {s.model} "
          f"(+{len(s.fallback_models)} fallbacks) | "
          f"{s.criterion} coverage target {s.target_pct:g}% | up to {s.max_test_iterations} iterations\n")

    for i, task in enumerate(tasks, start=1):
        task_dir = run_dir / f"task_{task.task_id}"
        if (task_dir / "result.json").exists():
            print(f"[{i}/{len(tasks)}] task {task.task_id}: already done, skipping")
            continue
        print(f"[{i}/{len(tasks)}] task {task.task_id}: {task.prompt[:90]}")
        try:
            result = process_task(task, s, code_agent, test_agent, exec_agent, task_dir)
        except DailyLimitError:
            print("\nFree-tier daily request limit reached. Progress is saved; resume later with:\n"
                  f"  python pipeline.py --run-name {run_name} "
                  + (f"--tasks {args.tasks}" if args.tasks else f"--start {args.start} --limit {args.limit}"))
            break
        except Exception as exc:  # keep going with the other problems
            print(f"  !! task {task.task_id} aborted: {exc}")
            (task_dir / "error.txt").write_text(str(exc), encoding="utf-8")
            continue
        (task_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print()

    write_summary(run_dir)


if __name__ == "__main__":
    main()
