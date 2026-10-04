"""Agent 1 - generates the unit of code (a single Python function) from the MBPP problem text."""
from __future__ import annotations

import ast
from dataclasses import dataclass

import prompts
from config import Settings
from dataset import Task
from llm_client import LLMClient
from utils import extract_code


@dataclass
class CodeGenResult:
    code: str
    attempts: int
    problem: str | None  # None when the code is structurally usable


def structural_problem(code: str, entry_point: str) -> str | None:
    """Only checks that the code parses and defines the expected function (not correctness)."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"SyntaxError: {exc.msg} (line {exc.lineno})"
    names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if entry_point not in names:
        return f"the code does not define a top-level function named `{entry_point}`"
    return None


class CodeGeneratorAgent:
    name = "code_generator"

    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm, self.s = llm, settings

    def generate(self, task: Task) -> CodeGenResult:
        code, problem = None, None
        for attempt in range(1, self.s.max_code_attempts + 1):
            raw = self.llm.chat(
                agent=self.name, task_id=task.task_id,
                system=prompts.CODE_GEN_SYSTEM,
                user=prompts.code_gen_user(task, code, problem),
                temperature=self.s.code_gen.temperature, max_tokens=self.s.code_gen.max_tokens,
            )
            code = extract_code(raw)
            problem = structural_problem(code, task.entry_point)
            if problem is None:
                return CodeGenResult(code, attempt, None)
            print(f"  [CodeGen] attempt {attempt} unusable: {problem}")
        return CodeGenResult(code, self.s.max_code_attempts, problem)
