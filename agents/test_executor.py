"""Agent 3 - executes the generated tests, measures coverage and gives a verdict.

Execution and coverage measurement are deterministic (pytest + coverage.py in a
subprocess). The LLM is only used to triage failing tests: is the failure a bug in
the code, or a wrong expected value in the test (the test-oracle problem)?

Verdicts
  PASS              all tests pass and the coverage target is met
  COVERAGE_NOT_MET  all tests pass but coverage is below target
  TEST_BUG          at least one failing test has a wrong expectation
  CODE_BUG_FOUND    failing tests are all attributed to bugs in the code
  ERROR             tests could not run (syntax/import error, timeout, no tests)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import prompts
from config import Settings
from dataset import Task
from llm_client import LLMClient
from sandbox import run_pytest

CONTINUE_VERDICTS = {"ERROR", "TEST_BUG", "COVERAGE_NOT_MET"}


class TestExecutorAgent:
    __test__ = False
    name = "test_executor"

    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm, self.s = llm, settings

    # ------------------------------------------------------------------ public API
    def execute(self, task: Task, code: str, tests: str, workdir: Path) -> dict:
        run = run_pytest(workdir, code, tests, timeout=self.s.pytest_timeout_s)
        cov = run.get("coverage")
        run["criterion"] = self.s.criterion
        run["criterion_pct"] = self._criterion_pct(cov)
        run["target_pct"] = self.s.target_pct
        run["target_met"] = self._target_met(cov)

        failures = [t for t in run["tests"] if t["status"] == "failed"]
        run["triage"] = self._triage(task, code, tests, failures) if failures else []
        run["verdict"], run["verdict_reason"] = self._verdict(run)
        run["feedback"] = self._feedback(run)
        (workdir / "execution_report.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
        return run

    @staticmethod
    def should_continue(report: dict) -> bool:
        if report["verdict"] in CONTINUE_VERDICTS:
            return True
        return report["verdict"] == "CODE_BUG_FOUND" and not report["target_met"]

    # ------------------------------------------------------------------ helpers
    def _criterion_pct(self, cov: dict | None) -> float:
        if not cov:
            return 0.0
        if self.s.criterion == "branch" and cov["branches"]:
            return cov["branch_pct"]
        return cov["statement_pct"]

    def _target_met(self, cov: dict | None) -> bool:
        if not cov:
            return False
        ok = cov["statement_pct"] >= self.s.target_pct
        if self.s.criterion == "branch":  # branch coverage subsumes statement coverage
            ok = ok and cov["branch_pct"] >= self.s.target_pct
        return ok

    def _triage(self, task: Task, code: str, tests: str, failures: list[dict]) -> list[dict]:
        try:
            raw = self.llm.chat(
                agent=self.name, task_id=task.task_id,
                system=prompts.TRIAGE_SYSTEM, user=prompts.triage_user(task, code, tests, failures),
                temperature=self.s.triage.temperature, max_tokens=self.s.triage.max_tokens,
            )
            match = re.search(r"\{.*\}", raw, re.S)
            items = json.loads(match.group(0))["failures"] if match else []
        except Exception as exc:  # triage is best-effort; fall back to "unknown"
            print(f"  [Executor] triage failed: {exc}")
            items = []
        by_name = {i.get("test"): i for i in items if isinstance(i, dict)}
        out = []
        for f in failures:
            item = by_name.get(f["name"], {})
            fault = item.get("fault") if item.get("fault") in ("code", "test") else "unknown"
            out.append({"test": f["name"], "fault": fault, "reason": item.get("reason", ""),
                        "message": f["message"]})
        return out

    def _verdict(self, run: dict) -> tuple[str, str]:
        if run["timed_out"]:
            return "ERROR", "test run timed out"
        if run["errors"] or run["total"] == 0:
            return "ERROR", "tests could not be collected or raised errors"
        test_faults = [t for t in run["triage"] if t["fault"] != "code"]
        code_faults = [t for t in run["triage"] if t["fault"] == "code"]
        cov_txt = f"{run['criterion']} coverage {run['criterion_pct']:g}% (target {run['target_pct']:g}%)"
        if not run["triage"]:
            if run["target_met"]:
                return "PASS", f"all {run['total']} tests passed, {cov_txt}"
            return "COVERAGE_NOT_MET", f"all {run['total']} tests passed, {cov_txt}"
        if test_faults:
            return "TEST_BUG", f"{len(test_faults)} failing test(s) have wrong expectations, {cov_txt}"
        return "CODE_BUG_FOUND", f"{len(code_faults)} test(s) expose a bug in the code, {cov_txt}"

    def _feedback(self, run: dict) -> str:
        """Message sent back to the test generator for the next iteration."""
        lines = [f"- Result: {run['passed']} passed, {run['failed']} failed, {run['errors']} errors "
                 f"({run['total']} tests). Verdict: {run['verdict']}."]
        cov = run.get("coverage")
        if cov:
            lines.append(f"- Statement coverage {cov['statement_pct']:g}%, branch coverage "
                         f"{cov['branch_pct']:g}% (target {run['target_pct']:g}% {run['criterion']}).")
            if cov["missing_lines"]:
                lines.append(f"- Lines never executed: {', '.join(map(str, cov['missing_lines']))}")
            if run["criterion"] == "branch" and cov["missing_branches"]:
                lines.append("- Decision outcomes never taken:")
                lines += [f"    * {b['text']}" for b in cov["missing_branches"]]
        if run["verdict"] == "ERROR":
            lines.append("- The test file could not run. pytest output:\n" + run["output_tail"][-1500:])
        wrong = [t for t in run["triage"] if t["fault"] != "code"]
        bugs = [t for t in run["triage"] if t["fault"] == "code"]
        if wrong:
            lines.append("- Failing tests with an INCORRECT expectation (fix or remove them):")
            lines += [f"    * {t['test']}: {t['message'].splitlines()[0] if t['message'] else ''} -- {t['reason']}"
                      for t in wrong]
        if bugs:
            lines.append("- Failing tests that expose a BUG in the code (keep them unchanged):")
            lines += [f"    * {t['test']}: {t['reason']}" for t in bugs]
        lines.append("Keep the passing tests, fix wrong expectations, and add tests that execute "
                     "the uncovered lines and decision outcomes.")
        return "\n".join(lines)
