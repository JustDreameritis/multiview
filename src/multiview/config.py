"""Configuration management — API keys and reviewer profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".multiview"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

PROVIDERS: dict[str, dict] = {
    "groq": {
        "env_var": "GROQ_API_KEY",
        "signup_url": "https://console.groq.com/keys",
        "name": "Groq",
    },
    "mistral": {
        "env_var": "MISTRAL_API_KEY",
        "signup_url": "https://console.mistral.ai/api-keys",
        "name": "Mistral",
    },
    "gemini": {
        "env_var": "GEMINI_API_KEY",
        "signup_url": "https://aistudio.google.com/apikey",
        "name": "Google Gemini",
    },
    "openrouter": {
        "env_var": "OPENROUTER_API_KEY",
        "signup_url": "https://openrouter.ai/keys",
        "name": "OpenRouter",
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "signup_url": "https://huggingface.co/settings/tokens",
        "name": "Hugging Face",
    },
}


@dataclass
class ReviewerProfile:
    name: str
    model: str
    provider: str
    system_prompt: str
    fallback_models: list[str] = field(default_factory=list)


DEFAULT_REVIEWERS: list[ReviewerProfile] = [
    ReviewerProfile(
        name="Security",
        model="groq/llama-4-scout-17b-16e-instruct",
        provider="groq",
        system_prompt=(
            "You are a security-focused code reviewer. Find vulnerabilities: "
            "injection flaws, auth bypasses, insecure deserialization, hardcoded "
            "secrets, path traversal, SSRF, XSS, SQL injection, command injection, "
            "race conditions, and OWASP Top 10 issues. For each finding, state the "
            "exact line(s), the vulnerability class, attack scenario, and a concrete fix. "
            "If the code is clean, say so. Do not invent issues."
        ),
    ),
    ReviewerProfile(
        name="Architecture",
        model="groq/gemma2-9b-it",
        provider="groq",
        system_prompt=(
            "You are an architecture reviewer. Evaluate: separation of concerns, "
            "coupling, cohesion, abstraction quality, error propagation, dependency "
            "direction, naming clarity, and whether the code follows the principle of "
            "least surprise. Flag God classes, circular dependencies, leaky abstractions, "
            "and missing error boundaries. Suggest concrete structural improvements."
        ),
    ),
    ReviewerProfile(
        name="Performance",
        model="mistral/mistral-small-latest",
        provider="mistral",
        system_prompt=(
            "You are a performance reviewer. Find: O(n^2+) algorithms that should be "
            "O(n log n) or O(n), unnecessary allocations, N+1 queries, missing caching "
            "opportunities, blocking I/O in async paths, memory leaks, unbounded growth, "
            "and hot-path inefficiencies. Quantify impact where possible (e.g. 'this loop "
            "allocates n strings where 1 suffices'). Suggest concrete optimizations."
        ),
    ),
    ReviewerProfile(
        name="Edge Cases",
        model="gemini/gemini-2.0-flash",
        provider="gemini",
        system_prompt=(
            "You are an edge-case and correctness reviewer. Find: unhandled None/null, "
            "empty collections, boundary values (0, -1, MAX_INT), Unicode edge cases, "
            "timezone bugs, floating-point comparison issues, off-by-one errors, race "
            "conditions in concurrent code, and missing input validation. For each, show "
            "the exact input that triggers the bug and the unexpected behavior."
        ),
    ),
    ReviewerProfile(
        name="Deep Reasoning",
        model="openrouter/deepseek/deepseek-r1:free",
        provider="openrouter",
        system_prompt=(
            "You are a deep-reasoning code reviewer. Think step by step about the code's "
            "correctness. Trace execution paths. Verify invariants. Check that error "
            "handling covers all failure modes. Look for subtle logic bugs that pass tests "
            "but fail in production. Verify that the code does what its name/comments claim."
        ),
    ),
    ReviewerProfile(
        name="Code Quality",
        model="huggingface/qwen3-32b",
        provider="huggingface",
        system_prompt=(
            "You are a code quality reviewer. Evaluate: readability, consistency, DRY "
            "violations, dead code, overly complex conditionals, magic numbers, missing "
            "type hints, docstring quality, test coverage gaps, and adherence to language "
            "idioms. Suggest specific refactors. Do not nitpick formatting — focus on "
            "substantive quality issues that affect maintainability."
        ),
    ),
]


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return yaml.safe_load(CONFIG_FILE.read_text()) or {}


def save_config(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(yaml.dump(data, default_flow_style=False))


def get_configured_providers() -> set[str]:
    config = load_config()
    keys = config.get("api_keys", {})
    return {p for p, k in keys.items() if k}
