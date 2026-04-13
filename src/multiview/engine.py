"""Review engine — parallel model dispatch and result collection."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import litellm

from .config import (
    DEFAULT_REVIEWERS,
    ReviewerProfile,
    load_config,
)

litellm.suppress_debug_info = True
litellm.set_verbose = False

REVIEW_USER_PROMPT = """Review the following code. For each issue found, respond in this exact format:

SEVERITY: CRITICAL|HIGH|MEDIUM|LOW
LOCATION: <file:line or file:line-line>
TITLE: <short title>
DESCRIPTION: <what's wrong and why it matters>
FIX: <concrete code change or approach>

---

If the code is clean from your review angle, respond with:
NO_ISSUES_FOUND

Code to review ({file_path}):
```
{code}
```"""


@dataclass
class Finding:
    severity: str
    location: str
    title: str
    description: str
    fix: str
    reviewers: list[str] = field(default_factory=list)


def _set_api_keys():
    """Load API keys from config into environment for LiteLLM."""
    config = load_config()
    keys = config.get("api_keys", {})
    env_map = {
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
    }
    for provider, env_var in env_map.items():
        if keys.get(provider) and not os.environ.get(env_var):
            os.environ[env_var] = keys[provider]


def _call_model(reviewer: ReviewerProfile, code: str, file_path: str) -> tuple[str, str | None, float]:
    """Call a single model and return (reviewer_name, response_text, duration)."""
    start = time.monotonic()
    prompt = REVIEW_USER_PROMPT.format(code=code, file_path=file_path)

    try:
        response = litellm.completion(
            model=reviewer.model,
            messages=[
                {"role": "system", "content": reviewer.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2048,
            timeout=60,
        )
        text = response.choices[0].message.content
        elapsed = time.monotonic() - start
        return reviewer.name, text, elapsed
    except Exception as e:
        elapsed = time.monotonic() - start
        return reviewer.name, None, elapsed


def _parse_findings(reviewer_name: str, raw: str) -> list[Finding]:
    """Parse structured findings from model response."""
    if not raw or "NO_ISSUES_FOUND" in raw:
        return []

    findings = []
    blocks = raw.split("---")

    for block in blocks:
        block = block.strip()
        if not block or "NO_ISSUES_FOUND" in block:
            continue

        finding = Finding(
            severity="MEDIUM",
            location="unknown",
            title="Untitled finding",
            description="",
            fix="",
            reviewers=[reviewer_name],
        )

        lines = block.split("\n")
        current_field = None

        for line in lines:
            line_stripped = line.strip()
            upper = line_stripped.upper()

            if upper.startswith("SEVERITY:"):
                val = line_stripped.split(":", 1)[1].strip().upper()
                if val in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                    finding.severity = val
                current_field = None
            elif upper.startswith("LOCATION:"):
                finding.location = line_stripped.split(":", 1)[1].strip()
                current_field = None
            elif upper.startswith("TITLE:"):
                finding.title = line_stripped.split(":", 1)[1].strip()
                current_field = None
            elif upper.startswith("DESCRIPTION:"):
                finding.description = line_stripped.split(":", 1)[1].strip()
                current_field = "description"
            elif upper.startswith("FIX:"):
                finding.fix = line_stripped.split(":", 1)[1].strip()
                current_field = "fix"
            elif current_field == "description":
                finding.description += " " + line_stripped
            elif current_field == "fix":
                finding.fix += " " + line_stripped

        if finding.title != "Untitled finding" or finding.description:
            findings.append(finding)

    return findings


def _similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity for deduplication."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    return len(intersection) / min(len(words_a), len(words_b))


def _deduplicate(all_findings: list[Finding], threshold: float = 0.55) -> list[Finding]:
    """Merge similar findings across reviewers."""
    merged: list[Finding] = []

    for finding in all_findings:
        matched = False
        for existing in merged:
            title_sim = _similarity(finding.title, existing.title)
            desc_sim = _similarity(finding.description, existing.description)
            if title_sim > threshold or desc_sim > threshold:
                for r in finding.reviewers:
                    if r not in existing.reviewers:
                        existing.reviewers.append(r)
                # Keep higher severity
                severity_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
                if severity_rank.get(finding.severity, 0) > severity_rank.get(existing.severity, 0):
                    existing.severity = finding.severity
                matched = True
                break
        if not matched:
            merged.append(finding)

    return merged


SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def run_review(
    code: str,
    file_path: str,
    reviewers: list[ReviewerProfile] | None = None,
    on_reviewer_done: callable = None,
) -> tuple[list[Finding], dict[str, float]]:
    """Run all reviewers in parallel against code, return deduplicated findings."""
    _set_api_keys()

    if reviewers is None:
        # Filter to only reviewers whose provider is configured
        config = load_config()
        keys = config.get("api_keys", {})
        reviewers = [r for r in DEFAULT_REVIEWERS if keys.get(r.provider)]

    if not reviewers:
        return [], {}

    all_findings: list[Finding] = []
    timings: dict[str, float] = {}
    errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(reviewers)) as pool:
        futures = {
            pool.submit(_call_model, r, code, file_path): r
            for r in reviewers
        }

        for future in as_completed(futures):
            reviewer = futures[future]
            name, response, elapsed = future.result()
            timings[name] = elapsed

            if response is None:
                errors[name] = "timeout or API error"
                if on_reviewer_done:
                    on_reviewer_done(name, False, elapsed)
                continue

            findings = _parse_findings(name, response)
            all_findings.extend(findings)
            if on_reviewer_done:
                on_reviewer_done(name, True, elapsed, len(findings))

    merged = _deduplicate(all_findings)
    merged.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    return merged, timings
