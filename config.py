"""Central configuration.

Every tunable parameter of the pipeline lives here so that it can be reported
(report item 2) and is dumped verbatim into each run folder as config.json.
Values can be overridden through environment variables / a .env file or CLI flags.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = PROJECT_ROOT / "runs"

CRITERIA = ("statement", "branch")


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    """Minimal .env loader (avoids an extra dependency). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api_key() -> str:
    key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit(
            "No API key found. Put OPENROUTER_API_KEY=... in a .env file next to "
            "pipeline.py (see .env.example) or set it as an environment variable."
        )
    return key


@dataclass
class AgentParams:
    temperature: float
    max_tokens: int


@dataclass
class Settings:
    # --- LLM endpoint (any OpenAI-compatible /chat/completions API) ---
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "google/gemma-4-31b-it:free"
    # Tried in order by OpenRouter when the primary model is rate-limited or down.
    # The model that actually answered is recorded for every call in llm_calls.jsonl.
    fallback_models: list[str] = field(default_factory=lambda: [
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
    ])
    top_p: float = 1.0
    seed: int | None = 42
    # The assignment forbids chain-of-thought, so model "thinking" is switched off.
    disable_reasoning: bool = True
    request_timeout_s: int = 180
    max_retries: int = 6
    min_interval_s: float = 3.5  # free tier allows ~20 requests/minute

    # --- per-agent sampling parameters ---
    code_gen: AgentParams = field(default_factory=lambda: AgentParams(temperature=0.2, max_tokens=1024))
    test_gen: AgentParams = field(default_factory=lambda: AgentParams(temperature=0.2, max_tokens=3000))
    triage: AgentParams = field(default_factory=lambda: AgentParams(temperature=0.0, max_tokens=800))

    # --- testing goal (user-specified coverage criterion) ---
    criterion: str = "branch"
    target_pct: float = 100.0
    max_test_iterations: int = 3  # generate -> execute -> feedback rounds per problem
    max_code_attempts: int = 2  # retries only when the code does not parse / lacks the function
    max_test_format_attempts: int = 3  # re-ask when a test reply is not a parseable test file
    pytest_timeout_s: int = 60

    # --- dataset ---
    dataset: str = "mbpp-sanitized"
    split: str = "test"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        s = cls()
        s.base_url = os.environ.get("LLM_BASE_URL", s.base_url).rstrip("/")
        s.model = os.environ.get("LLM_MODEL", s.model)
        if "LLM_FALLBACK_MODELS" in os.environ:  # comma-separated; empty disables fallback
            s.fallback_models = [m.strip() for m in os.environ["LLM_FALLBACK_MODELS"].split(",") if m.strip()]
        if "LLM_DISABLE_REASONING" in os.environ:
            s.disable_reasoning = os.environ["LLM_DISABLE_REASONING"].lower() in ("1", "true", "yes")
        if "LLM_MIN_INTERVAL_S" in os.environ:
            s.min_interval_s = float(os.environ["LLM_MIN_INTERVAL_S"])
        return s

    def to_dict(self) -> dict:
        return asdict(self)
