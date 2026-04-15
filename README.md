# multiview

Multi-model AI code review from your terminal. Six specialist reviewers, zero cost.

```
$ multiview review app.py

Reviewing app.py with 6 models...

  OK  Security         2.1s  (1 findings)
  OK  Architecture     1.8s  (0 findings)
  OK  Performance      3.2s  (2 findings)
  OK  Edge Cases       2.5s  (1 findings)
  OK  Deep Reasoning   4.1s  (1 findings)
  OK  Code Quality     2.9s  (0 findings)

┌───┬──────┬──────────────────┬──────────────────────────────────────┬────────────────┐
│ # │ Sev  │ Location         │ Issue                                │ Flagged by     │
├───┼──────┼──────────────────┼──────────────────────────────────────┼────────────────┤
│ 1 │ CRIT │ app.py:42        │ SQL Injection via f-string           │ Security,      │
│   │      │                  │ User input interpolated directly     │ Deep Reasoning │
│   │      │                  │ into SQL query. Use parameterized    │                │
│   │      │                  │ queries.                             │                │
├───┼──────┼──────────────────┼──────────────────────────────────────┼────────────────┤
│ 2 │ HIGH │ app.py:15-28     │ Unbounded list growth                │ Performance    │
│   │      │                  │ Results appended in loop without     │                │
│   │      │                  │ limit. Use generator or pagination.  │                │
├───┼──────┼──────────────────┼──────────────────────────────────────┼────────────────┤
│ 3 │ MED  │ app.py:67        │ Missing None check on user.email     │ Edge Cases     │
│   │      │                  │ AttributeError when user has no      │                │
│   │      │                  │ email set. Add: if user.email:       │                │
└───┴──────┴──────────────────┴──────────────────────────────────────┴────────────────┘

 Total: 3 issues  (1 CRITICAL, 1 HIGH, 1 MEDIUM)
```

## How it works

multiview sends your code to 6 free-tier AI models in parallel. Each model reviews from a specialist angle:

| Reviewer | Model | Focus |
|----------|-------|-------|
| Security | Llama 3.3 70B | OWASP Top 10, injection, auth, secrets |
| Architecture | Gemma 2 9B | Coupling, cohesion, abstraction, naming |
| Performance | Mistral Small | O(n²), N+1, allocations, caching |
| Edge Cases | Gemini 2.0 Flash | Null, boundaries, Unicode, off-by-one |
| Deep Reasoning | DeepSeek R1 | Logic bugs, invariant violations, correctness |
| Code Quality | Qwen 2.5 Coder | DRY, dead code, idioms, readability |

Findings are deduplicated across models, ranked by severity, and show which reviewers flagged each issue.

## Install

```bash
pip install multiview
```

Or from source:
```bash
git clone https://github.com/JustDreameritis/multiview
cd multiview
pip install -e .
```

## Setup

```bash
multiview setup
```

Walks you through getting free API keys from each provider. Direct links to signup pages. No credit card needed.

**Providers used:**
- [Groq](https://console.groq.com/keys) - Security & Architecture
- [Mistral](https://console.mistral.ai/api-keys) - Performance
- [Google AI Studio](https://aistudio.google.com/apikey) - Edge Cases
- [OpenRouter](https://openrouter.ai/keys) - Deep Reasoning
- [HuggingFace](https://huggingface.co/settings/tokens) - Code Quality

## Usage

### Code Review

```bash
# Review a file
multiview review app.py

# Review a directory
multiview review src/

# JSON output for CI/CD
multiview review app.py --json

# Markdown output for PR comments
multiview review app.py --markdown

# Use specific reviewers only
multiview review app.py --model security --model performance

# Check which reviewers are active
multiview status
```

### Multi-Perspective Questions

```bash
# Ask a question to 6 specialist perspectives
multiview ask "What causes inflation?"

# JSON output
multiview ask "Should I use microservices?" --json
```

Each question is analyzed by 6 perspectives in parallel:
- **Factual Analyst** — verifies claims, cites established knowledge
- **Devil's Advocate** — challenges assumptions, finds weaknesses
- **Practical Advisor** — focuses on what you should actually DO
- **Technical Expert** — provides deep domain knowledge
- **Risk Assessor** — identifies what could go wrong
- **Synthesizer** — merges all views into balanced answer

Output shows each perspective, then a **CONSENSUS** section with:
- What they agree on
- Where they disagree
- Synthesized answer
- Confidence score (HIGH/MEDIUM/LOW)

## Output formats

- **Terminal** (default): Rich table with colors and severity indicators
- **JSON** (`--json`): Machine-readable for CI pipelines
- **Markdown** (`--markdown`): Paste into PR comments

## Why multi-model?

1. **Different models catch different bugs.** DeepSeek finds logic errors Claude misses. Gemini catches Unicode edge cases Llama doesn't flag.

2. **Consensus = confidence.** When 3+ models flag the same issue, you know it's real.

3. **Specialist prompts matter.** A security-focused system prompt makes the model actually look for OWASP issues instead of generic "improvements."

## License

MIT
