"""Agent 2 - generates a pytest suite aimed at the user-specified coverage criterion.

On iterations 2+ it receives the previous suite plus the executor's feedback
(uncovered lines/branches, wrong expectations) and returns a revised suite.
A reply that is not a usable test file (e.g. prose instead of code, or cut off at the
token limit) is rejected and re-requested before it reaches the executor.
"""
from __future__ import annotations

import ast

import prompts
from config import Settings
from dataset import Task
from llm_client import LLMClient
from utils import extract_code


def structural_problem(tests: str) -> str | None:
    try:
        tree = ast.parse(tests)
    except SyntaxError as exc:
        return f"the reply is not valid Python (SyntaxError: {exc.msg}, line {exc.lineno})"
    if not any(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in tree.body):
        return "the reply contains no `test_` functions"
    return None


class TestGeneratorAgent:
    __test__ = False  # stop pytest from collecting this class
    name = "test_generator"

    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm, self.s = llm, settings
        self.last_attempts = 0

    def generate(self, task: Task, code: str, previous_tests: str | None = None,
                 feedback: str | None = None) -> str:
        user = prompts.test_gen_user(task, code, previous_tests, feedback)
        problem = None
        for attempt in range(1, self.s.max_test_format_attempts + 1):
            self.last_attempts = attempt
            raw = self.llm.chat(
                agent=self.name, task_id=task.task_id,
                system=prompts.test_gen_system(self.s.criterion, self.s.target_pct),
                user=user if problem is None else user + prompts.format_retry_note(problem),
                temperature=self.s.test_gen.temperature, max_tokens=self.s.test_gen.max_tokens,
            )
            tests = extract_code(raw)
            if "from solution import" not in tests and "import solution" not in tests:
                tests = "from solution import *\n" + tests
            problem = structural_problem(tests)
            if problem is None:
                break
            print(f"  [TestGen]  reply {attempt} unusable ({problem}); asking again")
        return tests
