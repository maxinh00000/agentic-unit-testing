"""MBPP (Mostly Basic Python Problems) loader.

Uses the hand-verified *sanitized* MBPP release (427 problems) from
https://github.com/google-research/google-research/tree/master/mbpp
Task-id ranges follow the paper's splits: prompt 1-10, test 11-510,
validation 511-600, train 601-974.
"""
from __future__ import annotations

import ast
import builtins
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import requests

from config import DATA_DIR

MBPP_SANITIZED_URL = (
    "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/sanitized-mbpp.json"
)
SPLITS = {"prompt": (1, 10), "test": (11, 510), "validation": (511, 600), "train": (601, 974)}


@dataclass
class Task:
    task_id: int
    prompt: str
    reference_code: str
    test_list: list[str]
    test_imports: list[str] = field(default_factory=list)
    entry_point: str = ""

    @property
    def example_test(self) -> str:
        return self.test_list[0]


def _entry_point(test: str, imports: list[str], reference_code: str = "") -> str:
    """Name of the function under test: the first function called in the assert that the
    reference solution defines (handles names like `sum` that shadow builtins); otherwise
    the first non-builtin, non-imported function called."""
    called = [n.func.id for n in ast.walk(ast.parse(test))
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    try:
        with warnings.catch_warnings():  # some solutions have regexes with invalid escapes
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(reference_code)
        defined = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    except SyntaxError:
        defined = set()
    for name in called:
        if name in defined:
            return name
    imported = set()
    for line in imports:
        try:
            for node in ast.walk(ast.parse(line)):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imported.update((a.asname or a.name).split(".")[0] for a in node.names)
        except SyntaxError:
            pass
    for name in called:
        if not hasattr(builtins, name) and name not in imported:
            return name
    raise ValueError(f"cannot find function under test in: {test}")


def ensure_mbpp(path: Path = DATA_DIR / "sanitized-mbpp.json") -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[dataset] downloading MBPP (sanitized) -> {path}")
        resp = requests.get(MBPP_SANITIZED_URL, timeout=60)
        resp.raise_for_status()
        path.write_bytes(resp.content)
    return path


def load_mbpp(split: str = "test") -> list[Task]:
    raw = json.loads(ensure_mbpp().read_text(encoding="utf-8"))
    lo, hi = SPLITS[split]
    tasks = []
    for row in sorted(raw, key=lambda r: r["task_id"]):
        if not lo <= row["task_id"] <= hi:
            continue
        imports = row.get("test_imports") or []
        tasks.append(
            Task(
                task_id=row["task_id"],
                prompt=row.get("prompt") or row.get("text", ""),
                reference_code=row["code"],
                test_list=row["test_list"],
                test_imports=imports,
                entry_point=_entry_point(row["test_list"][0], imports, row["code"]),
            )
        )
    return tasks


def select_tasks(tasks: list[Task], ids: list[int] | None, start: int, limit: int) -> list[Task]:
    if ids:
        by_id = {t.task_id: t for t in tasks}
        missing = [i for i in ids if i not in by_id]
        if missing:
            raise SystemExit(f"task ids not in this split: {missing}")
        return [by_id[i] for i in ids]
    return tasks[start : start + limit]
