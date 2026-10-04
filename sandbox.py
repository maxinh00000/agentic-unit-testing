"""Runs pytest (+ coverage.py) in an isolated folder and parses the results.

Each run gets its own directory containing solution.py, the test file, a blank
pytest.ini (so no outer config leaks in), the JUnit XML report and coverage.json.
Tests execute in a subprocess with a timeout so generated infinite loops cannot hang the pipeline.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from utils import truncate

# Collect only tests defined in the test file itself. Otherwise a function under test whose
# name starts with "test_" (e.g. MBPP's `test_duplicate`), imported via `from solution import *`,
# is wrongly collected as a test and errors with "fixture not found".
CONFTEST = '''def pytest_collection_modifyitems(items):
    def own(item):
        mod = getattr(item, "module", None)
        obj = getattr(item, "obj", None)
        return mod is None or getattr(obj, "__module__", mod.__name__) == mod.__name__
    items[:] = [i for i in items if own(i)]
'''


def run_pytest(workdir: Path, code: str, tests: str, *, test_file: str = "test_solution.py",
               with_coverage: bool = True, timeout: int = 60) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (workdir / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (workdir / "solution.py").write_text(code, encoding="utf-8")
    (workdir / test_file).write_text(tests, encoding="utf-8")
    junit = workdir / "junit.xml"
    cov_json = workdir / "coverage.json"
    for stale in (junit, cov_json, workdir / ".coverage"):
        stale.unlink(missing_ok=True)

    cmd = [sys.executable, "-m", "pytest", test_file, "-q", "-p", "no:cacheprovider",
           "--confcutdir=.", f"--junitxml={junit.name}"]
    if with_coverage:
        cmd += ["--cov=solution", "--cov-branch", f"--cov-report=json:{cov_json.name}",
                "--cov-report=term-missing"]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}

    timed_out = False
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout, env=env)
        output, exit_code = proc.stdout + proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out, exit_code = True, None
        output = f"TIMEOUT after {timeout}s (possible infinite loop)\n" + str(exc.stdout or "")
    (workdir / "pytest_output.txt").write_text(output, encoding="utf-8")

    tests_info = _parse_junit(junit) if junit.exists() else []
    result = {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "tests": tests_info,
        "total": len(tests_info),
        "passed": sum(t["status"] == "passed" for t in tests_info),
        "failed": sum(t["status"] == "failed" for t in tests_info),
        "errors": sum(t["status"] == "error" for t in tests_info),
        "output_tail": truncate(output[-3000:], 3000),
    }
    if with_coverage:
        result["coverage"] = _parse_coverage(cov_json, code) if cov_json.exists() else None
    return result


def _parse_junit(path: Path) -> list[dict]:
    tests = []
    for tc in ET.parse(path).getroot().iter("testcase"):
        status, message = "passed", ""
        if tc.find("skipped") is not None:
            status = "skipped"
        for tag, label in (("failure", "failed"), ("error", "error")):
            el = tc.find(tag)
            if el is not None:
                status = label
                message = ((el.get("message") or "") + "\n" + (el.text or "")).strip()
        tests.append({"name": tc.get("name"), "status": status, "message": truncate(message, 1500)})
    return tests


def _parse_coverage(path: Path, code: str) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    entry = next((v for k, v in data.get("files", {}).items() if Path(k).name == "solution.py"), None)
    if entry is None:
        return None
    summ = entry["summary"]
    n_stmt, c_stmt = summ["num_statements"], summ["covered_lines"]
    n_br, c_br = summ.get("num_branches", 0), summ.get("covered_branches", 0)
    lines = code.splitlines()

    def src(n: int) -> str:
        return lines[n - 1].strip() if 0 < n <= len(lines) else ""

    missing_branches = []
    for frm, to in entry.get("missing_branches", []):
        dest = "function exit" if to < 0 else f"line {to}"
        missing_branches.append({"from": frm, "to": to,
                                 "text": f"line {frm} (`{src(frm)}`) -> {dest} never taken"})
    return {
        "statements": n_stmt,
        "covered_statements": c_stmt,
        "statement_pct": round(100.0 * c_stmt / n_stmt, 2) if n_stmt else 100.0,
        "branches": n_br,
        "covered_branches": c_br,
        "branch_pct": round(100.0 * c_br / n_br, 2) if n_br else 100.0,
        "missing_lines": entry.get("missing_lines", []),
        "missing_branches": missing_branches,
    }


def reference_test_file(asserts: list[str], imports: list[str]) -> str:
    """Wrap each MBPP assert in its own test function so we get per-assert results."""
    parts = ["from solution import *", *imports, ""]
    for i, a in enumerate(asserts, start=1):
        parts += [f"def test_reference_{i}():", f"    {a}", ""]
    return "\n".join(parts)
