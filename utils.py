"""Small helpers shared by the agents."""
from __future__ import annotations

import re

_CODE_BLOCK_RE = re.compile(r"```[ \t]*(?:python|py|python3)?[ \t]*\r?\n(.*?)```", re.S | re.I)
_THINK_RE = re.compile(r"<think>.*?</think>", re.S | re.I)


def extract_code(text: str) -> str:
    """Pull Python source out of an LLM reply (fenced block preferred)."""
    text = _THINK_RE.sub("", text or "")
    blocks = _CODE_BLOCK_RE.findall(text)
    if blocks:
        return max(blocks, key=len).strip() + "\n"
    if "```" in text:  # unterminated fence: take everything after it
        text = text.split("```", 1)[1]
        first_line, _, rest = text.partition("\n")
        if first_line.strip().lower() in ("", "python", "py", "python3"):
            text = rest
    return text.strip() + "\n"


def number_lines(code: str) -> str:
    """Prefix each line with its 1-based number (matches coverage.py line numbers)."""
    return "\n".join(f"{i:>3} | {line}" for i, line in enumerate(code.splitlines(), start=1))


def truncate(text: str, limit: int = 1500) -> str:
    text = text or ""
    return text if len(text) <= limit else text[:limit] + f"\n... [truncated {len(text) - limit} chars]"
