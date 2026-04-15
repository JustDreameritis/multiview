"""Ask engine - Multi-perspective question answering."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import litellm

from .config import load_config

litellm.suppress_debug_info = True
litellm.set_verbose = False


@dataclass
class Perspective:
    name: str
    model: str
    provider: str
    system_prompt: str


@dataclass
class PerspectiveResponse:
    name: str
    response: str
    elapsed: float
    success: bool


# 6 specialist perspectives for multi-angle analysis
ASK_PERSPECTIVES: list[Perspective] = [
    Perspective(
        name="Factual Analyst",
        model="anthropic/claude-sonnet-4-20250514",
        provider="anthropic",
        system_prompt=(
            "You are a Factual Analyst. Your role is to verify claims and cite what is "
            "established. Distinguish between facts, theories, and opinions. Reference "
            "scientific consensus where applicable. If something is uncertain or debated, "
            "say so clearly. Never speculate without labeling it as speculation. "
            "Be precise and cite sources of knowledge (e.g., 'According to economic theory...', "
            "'Studies have shown...'). Keep your response focused and under 200 words."
        ),
    ),
    Perspective(
        name="Devil's Advocate",
        model="xai/grok-3-fast-beta",
        provider="xai",
        system_prompt=(
            "You are a Devil's Advocate. Your role is to argue the opposite position and "
            "find weaknesses in the conventional view. Challenge assumptions. Point out "
            "what's being overlooked or oversimplified. Present the strongest counterarguments "
            "even if you don't personally agree with them. Be intellectually rigorous but "
            "not contrarian for its own sake. Your goal is to stress-test ideas, not to be "
            "disagreeable. Keep your response focused and under 200 words."
        ),
    ),
    Perspective(
        name="Practical Advisor",
        model="anthropic/claude-sonnet-4-20250514",
        provider="anthropic",
        system_prompt=(
            "You are a Practical Advisor. Your role is to focus on actionable guidance. "
            "What should someone actually DO given this question? Provide concrete steps, "
            "real-world applications, and practical recommendations. Skip theory and "
            "focus on implementation. Consider different situations and audiences. "
            "Be direct and useful. Keep your response focused and under 200 words."
        ),
    ),
    Perspective(
        name="Technical Expert",
        model="xai/grok-3-fast-beta",
        provider="xai",
        system_prompt=(
            "You are a Technical Expert with deep domain knowledge. Provide the detailed, "
            "nuanced explanation that an expert in this field would give. Use proper "
            "terminology but explain it. Cover mechanisms, causal chains, and underlying "
            "principles. Don't oversimplify. Address edge cases and exceptions. "
            "If the question spans multiple domains, address each. Keep your response "
            "focused and under 200 words."
        ),
    ),
    Perspective(
        name="Risk Assessor",
        model="anthropic/claude-sonnet-4-20250514",
        provider="anthropic",
        system_prompt=(
            "You are a Risk Assessor. Your role is to identify what could go wrong and "
            "what's being missed. Consider unintended consequences, second-order effects, "
            "and hidden risks. What are the failure modes? What assumptions might be wrong? "
            "What would cause this to fail? Be thorough but not paranoid. Focus on risks "
            "that actually matter. Keep your response focused and under 200 words."
        ),
    ),
    Perspective(
        name="Synthesizer",
        model="xai/grok-3-fast-beta",
        provider="xai",
        system_prompt=(
            "You are a Synthesizer. Your role is to provide a balanced, comprehensive "
            "answer that integrates multiple viewpoints. Acknowledge complexity and nuance. "
            "Present the mainstream view but note significant dissenting positions. "
            "Identify what we know confidently vs. what remains uncertain. Give a clear "
            "bottom-line answer while respecting complexity. Keep your response focused "
            "and under 200 words."
        ),
    ),
]


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
        "anthropic": "ANTHROPIC_API_KEY",
        "xai": "XAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }
    for provider, env_var in env_map.items():
        if keys.get(provider) and not os.environ.get(env_var):
            os.environ[env_var] = keys[provider]


def _call_perspective(perspective: Perspective, question: str) -> PerspectiveResponse:
    """Call a single model with its specialist prompt."""
    start = time.monotonic()

    user_prompt = f"""Question: {question}

Provide your perspective as a {perspective.name}. Be concise and direct."""

    try:
        response = litellm.completion(
            model=perspective.model,
            messages=[
                {"role": "system", "content": perspective.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
            timeout=60,
        )
        text = response.choices[0].message.content
        elapsed = time.monotonic() - start
        return PerspectiveResponse(
            name=perspective.name,
            response=text.strip(),
            elapsed=elapsed,
            success=True,
        )
    except Exception as e:
        elapsed = time.monotonic() - start
        return PerspectiveResponse(
            name=perspective.name,
            response=f"Error: {str(e)}",
            elapsed=elapsed,
            success=False,
        )


def _generate_consensus(question: str, responses: list[PerspectiveResponse]) -> str:
    """Generate consensus analysis from all perspectives."""
    _set_api_keys()

    # Build context from all responses
    perspectives_text = "\n\n".join([
        f"**{r.name}:**\n{r.response}"
        for r in responses if r.success
    ])

    prompt = f"""You are analyzing multiple expert perspectives on a question.

QUESTION: {question}

PERSPECTIVES:
{perspectives_text}

Analyze these perspectives and provide:

1. **AGREEMENT** - What do most perspectives agree on? (2-3 key points)

2. **DISAGREEMENT** - Where do perspectives differ? What's contested? (2-3 key points)

3. **SYNTHESIS** - Given all perspectives, what's the most complete answer? (3-4 sentences)

4. **CONFIDENCE** - Rate overall confidence in the synthesis (HIGH/MEDIUM/LOW) and explain why.

Be concise. Focus on substance, not meta-commentary."""

    try:
        response = litellm.completion(
            model="anthropic/claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800,
            timeout=90,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating consensus: {str(e)}"


def get_configured_perspectives() -> list[Perspective]:
    """Return perspectives that have configured API keys."""
    config = load_config()
    keys = config.get("api_keys", {})
    return [p for p in ASK_PERSPECTIVES if keys.get(p.provider)]


def ask(question: str, on_perspective_done: callable = None) -> tuple[list[PerspectiveResponse], str]:
    """Ask a question to all configured perspectives in parallel, then generate consensus."""
    _set_api_keys()

    perspectives = get_configured_perspectives()
    if not perspectives:
        return [], "No perspectives available. Run 'multiview setup' first."

    responses: list[PerspectiveResponse] = []

    # Run all perspectives in parallel
    with ThreadPoolExecutor(max_workers=len(perspectives)) as pool:
        futures = {
            pool.submit(_call_perspective, p, question): p
            for p in perspectives
        }

        for future in as_completed(futures):
            result = future.result()
            responses.append(result)
            if on_perspective_done:
                on_perspective_done(result.name, result.success, result.elapsed)

    # Sort by original order
    name_order = {p.name: i for i, p in enumerate(ASK_PERSPECTIVES)}
    responses.sort(key=lambda r: name_order.get(r.name, 99))

    # Generate consensus from successful responses
    successful = [r for r in responses if r.success]
    if len(successful) >= 2:
        consensus = _generate_consensus(question, successful)
    else:
        consensus = "Not enough perspectives responded successfully to generate consensus."

    return responses, consensus
