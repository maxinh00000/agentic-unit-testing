"""Thin client for an OpenAI-compatible /chat/completions endpoint (OpenRouter by default).

No agent framework is used: each agent is just a system prompt + user prompt sent
through `LLMClient.chat`. Every request and response is appended to llm_calls.jsonl
so the exact prompts and settings can be shown in the report.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests

from config import Settings, api_key


class DailyLimitError(RuntimeError):
    """Free-tier daily quota exhausted - retrying today is pointless."""


class LLMClient:
    def __init__(self, settings: Settings, log_file: Path):
        self.s = settings
        self.log_file = log_file
        self.key = api_key()
        self._last_call = 0.0
        # Some reasoning models refuse to turn thinking off; then we keep it minimal and hidden.
        self._reasoning = {"enabled": False} if settings.disable_reasoning else None
        self.calls = 0

    def _body(self, system: str, user: str, temperature: float, max_tokens: int) -> dict:
        body = {
            "model": self.s.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.s.top_p,
        }
        if self.s.seed is not None:
            body["seed"] = self.s.seed
        if "openrouter.ai" in self.s.base_url:
            if self._reasoning is not None:
                body["reasoning"] = self._reasoning
            fallbacks = [m for m in self.s.fallback_models if m != self.s.model]
            if fallbacks:  # OpenRouter model routing: next model is tried on rate limits/errors
                body["models"] = [self.s.model, *fallbacks]
        return body

    def _throttle(self) -> None:
        wait = self.s.min_interval_s - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def chat(self, *, agent: str, task_id: int | str, system: str, user: str,
             temperature: float, max_tokens: int) -> str:
        url = f"{self.s.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "X-Title": "CSE731 AI-assisted unit testing",
        }
        started = time.monotonic()
        error, data, attempt, body = None, None, 0, None
        for attempt in range(1, self.s.max_retries + 1):
            body = self._body(system, user, temperature, max_tokens)
            self._throttle()
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=self.s.request_timeout_s)
            except requests.RequestException as exc:
                error = f"network error: {exc}"
                time.sleep(min(60, 5 * 2 ** (attempt - 1)))
                continue

            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:  # OpenRouter can return 200 with an upstream error payload
                    error = json.dumps(data["error"])[:500]
                    time.sleep(min(60, 5 * 2 ** (attempt - 1)))
                    continue
                content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
                if content:
                    error = None
                    break
                error = "empty response content"
                continue

            text = resp.text[:800]
            error = f"HTTP {resp.status_code}: {text}"
            if resp.status_code == 400 and "reasoning" in text.lower() and self._reasoning == {"enabled": False}:
                print("  [llm] model cannot disable reasoning; falling back to minimal, hidden reasoning")
                self._reasoning = {"effort": "low", "exclude": True}
                continue
            if resp.status_code == 429 and "per-day" in text.lower():
                self._log(agent, task_id, body, system, user, None, None, started, attempt, error)
                raise DailyLimitError(text)
            if resp.status_code in (408, 429, 500, 502, 503, 504):
                retry_after = resp.headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else min(90, 10 * 2 ** (attempt - 1))
                try:
                    err = resp.json()["error"]
                    reason = (err.get("metadata") or {}).get("raw") or err["message"]
                except Exception:
                    reason = text
                print(f"  [llm] {resp.status_code} from API ({reason[:110]}), retrying in {delay:.0f}s "
                      f"(attempt {attempt}/{self.s.max_retries})")
                time.sleep(delay)
                continue
            break  # other 4xx: not retryable

        content = None
        if data and not error:
            content = data["choices"][0]["message"]["content"]
        self._log(agent, task_id, body, system, user, content, data, started, attempt, error)
        if content is None:
            raise RuntimeError(f"LLM call failed for {agent} (task {task_id}): {error}")
        self.calls += 1
        return content

    def _log(self, agent, task_id, body, system, user, content, data, started, attempts, error) -> None:
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": agent,
            "task_id": task_id,
            "model": (data or {}).get("model", self.s.model),
            "params": {k: v for k, v in (body or {}).items() if k != "messages"},
            "system_prompt": system,
            "user_prompt": user,
            "response": content,
            "usage": (data or {}).get("usage"),
            "latency_s": round(time.monotonic() - started, 2),
            "attempts": attempts,
            # OpenRouter error bodies include the account's user id; keep it out of shareable logs
            "error": re.sub(r"user_[A-Za-z0-9]{8,}", "user_<redacted>", error) if error else None,
        }
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
