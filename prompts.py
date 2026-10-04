"""All prompts used by the three agents.

System prompts are fixed; user prompts are filled in per problem / per iteration.
No chain-of-thought instructions are used anywhere: every agent is asked for the
final artefact (code, tests or a JSON verdict) directly.
"""
from __future__ import annotations

from dataset import Task
from utils import number_lines

CRITERION_TEXT = {
    "statement": (
        "STATEMENT COVERAGE - every executable statement (line) of the module `solution` "
        "must be executed by at least one test."
    ),
    "branch": (
        "BRANCH (DECISION) COVERAGE - every decision in the module `solution` must be driven "
        "to each of its outcomes at least once: the True and the False outcome of every "
        "`if`/`elif`/`while`/conditional expression, and for every `for`/`while` loop both "
        "entering the loop body and finishing/skipping the loop. Every statement must also run."
    ),
}

# ---------------------------------------------------------------- Agent 1: code generator
CODE_GEN_SYSTEM = """You are the Code Generator agent in a unit-testing pipeline.
Write a correct, self-contained Python 3 implementation of the programming problem you are given.

Rules:
- Reply with a single ```python code block and nothing else.
- Define the function with exactly the name and parameters used in the example call.
- Use only the Python standard library; put any imports at the top of the code.
- Do not read input, print, or include tests, usage examples or a __main__ block."""


def code_gen_user(task: Task, previous_code: str | None = None, problem: str | None = None) -> str:
    msg = (
        f"Problem:\n{task.prompt}\n\n"
        f"Example call that the function must satisfy:\n{task.example_test}\n"
    )
    if previous_code is not None:
        msg += (
            f"\nYour previous answer could not be used:\n```python\n{previous_code}```\n"
            f"Reason: {problem}\nReturn a corrected implementation.\n"
        )
    return msg + "\nReply with only the ```python code block.\n"


# ---------------------------------------------------------------- Agent 2: test generator
TEST_GEN_SYSTEM = """You are the Test Case Generator agent in a unit-testing pipeline.
You receive a problem specification and a Python implementation saved as the module `solution`.
Write a pytest test file for it that meets the test requirement below.

Test requirement: {criterion_text}
Target: at least {target:g}% {criterion} coverage of the module `solution`.

Rules:
- Reply with a single ```python code block and nothing else.
- The first line must be `from solution import *`; add `import pytest` only if you use it.
- One scenario per test function, named `test_<scenario>`; every test must assert a concrete expected value.
- Derive every expected value from the problem specification, not by re-running the implementation's logic. If the implementation looks wrong for an input, still assert what the specification requires.
- Use pytest.raises only when the specification or the code clearly raises for that input.
- Tests must be deterministic and fast: no randomness, printing, file or network access, sleeping or mocking.
- Do not redefine or copy the function under test."""


def test_gen_system(criterion: str, target: float) -> str:
    return TEST_GEN_SYSTEM.format(criterion_text=CRITERION_TEXT[criterion], target=target, criterion=criterion)


def test_gen_user(task: Task, code: str, previous_tests: str | None = None, feedback: str | None = None) -> str:
    msg = (
        f"Problem specification:\n{task.prompt}\n\n"
        f"Example from the specification:\n{task.example_test}\n\n"
        f"Function under test (module `solution`; line numbers are for reference only):\n"
        f"{number_lines(code)}\n"
    )
    if previous_tests is not None:
        msg += (
            f"\nYour previous test file:\n```python\n{previous_tests}```\n\n"
            f"Execution feedback from the Test Executor agent:\n{feedback}\n\n"
            "Return the complete revised test file.\n"
        )
    return msg + "\nReply with only the complete test file in one ```python code block, with no explanation.\n"


def format_retry_note(problem: str) -> str:
    """Appended to the same user prompt when the previous reply was not a usable test file."""
    return (f"\nYour previous reply could not be used: {problem}. Do not explain or discuss. "
            "Reply with only the complete test file in one ```python code block.\n")


# ---------------------------------------------------------------- Agent 3: executor (failure triage)
TRIAGE_SYSTEM = """You are the Test Executor agent in a unit-testing pipeline. The tests have been run; some failed.
For every failing test decide, using the problem specification as the source of truth, whether the failure is caused by:
- "code": the function returns something the specification does not allow (the test is right), or
- "test": the test's expected value or assumption contradicts the specification (the code is right for that input).

Reply with JSON only, in exactly this shape:
{"failures": [{"test": "<test name>", "fault": "code" or "test", "reason": "<one short sentence>"}]}"""


def triage_user(task: Task, code: str, tests: str, failures: list[dict]) -> str:
    listed = "\n\n".join(f"### {f['name']}\n{f['message']}" for f in failures)
    return (
        f"Problem specification:\n{task.prompt}\n\n"
        f"Example from the specification:\n{task.example_test}\n\n"
        f"Function under test (module `solution`):\n```python\n{code}```\n\n"
        f"Test file:\n```python\n{tests}```\n\n"
        f"Failing tests and pytest messages:\n{listed}\n\n"
        "Reply with only the JSON object.\n"
    )


def render_all(criterion: str, target: float) -> str:
    """Markdown dump of every prompt template (written into each run folder for the report)."""
    return "\n\n".join([
        "# Prompt templates",
        "## Agent 1 - Code Generator\n### System prompt\n```text\n" + CODE_GEN_SYSTEM + "\n```",
        "### User prompt template\n```text\nProblem:\n{problem text}\n\nExample call that the function must satisfy:\n"
        "{first MBPP assert}\n\n[only on retry:]\nYour previous answer could not be used:\n{code}\n"
        "Reason: {syntax error / missing function}\nReturn a corrected implementation.\n\n"
        "Reply with only the ```python code block.\n```",
        "## Agent 2 - Test Case Generator\n### System prompt\n```text\n" + test_gen_system(criterion, target) + "\n```",
        "### User prompt template\n```text\nProblem specification:\n{problem text}\n\nExample from the specification:\n"
        "{first MBPP assert}\n\nFunction under test (module `solution`; line numbers are for reference only):\n"
        "{numbered code}\n\n[iterations 2+ only:]\nYour previous test file:\n{tests}\n\n"
        "Execution feedback from the Test Executor agent:\n{feedback}\n\nReturn the complete revised test file.\n\n"
        "Reply with only the complete test file in one ```python code block, with no explanation.\n\n"
        "[only if the previous reply was not a parseable test file:]\n"
        + format_retry_note("{syntax error / no test_ functions}").strip() + "\n```",
        "## Agent 3 - Test Executor (failure triage)\n### System prompt\n```text\n" + TRIAGE_SYSTEM + "\n```",
        "### User prompt template\n```text\nProblem specification:\n{problem text}\n\nExample from the specification:\n"
        "{first MBPP assert}\n\nFunction under test (module `solution`):\n{code}\n\nTest file:\n{tests}\n\n"
        "Failing tests and pytest messages:\n### {test name}\n{assertion message}\n...\n\n"
        "Reply with only the JSON object.\n```",
    ])
