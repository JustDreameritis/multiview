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

                          multiview: app.py
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
  Timings: Architecture: 1.8s | Security: 2.1s | Edge Cases: 2.5s | ...
```

## How it works

multiview sends your code to 6 free-tier AI models in parallel. Each model reviews from a specialist angle:

| Reviewer | Model | Focus |
|----------|-------|-------|
| Security | Groq/Llama 4 Scout | OWASP Top 10, injection, auth, secrets |
| Architecture | Groq/Gemma 2 9B | Coupling, cohesion, abstraction, naming |
| Performance | Mistral Small | O(n^2), N+1, allocations, caching |
| Edge Cases | Gemini 2.0 Flash | Null, boundaries, Unicode, off-by-one |
| Deep Reasoning | DeepSeek R1 | Logic bugs, invariant violations, correctness |
| Code Quality | HuggingFace/Qwen 32B | DRY, dead code, idioms, readability |

Findings are deduplicated across models (fuzzy match), ranked by severity, and shown with which models agreed on each issue.

## Install

```bash
pip install multiview
# or from source:
git clone https://github.com/JustDreameritis/multiview && cd multiview
pip install -e .
```

## Setup (2 minutes)

```bash
multiview setup
```

Walks you through grabbing free API keys from each provider. Direct links to signup pages. No credit card needed for any of them.

## Usage

```bash
# Review a file
multiview review app.py

# Review a directory
multiview review src/

# JSON output (for CI/CD)
multiview review app.py --json

# Markdown output (for PRs)
multiview review app.py --markdown

# Use specific reviewers only
multiview review app.py --model security --model performance

# Check which reviewers are active
multiview status
```

## Output formats

- **Terminal** (default): Rich table with colors and severity indicators
- **JSON** (`--json`): Machine-readable for CI pipelines
- **Markdown** (`--markdown`): Paste into PR comments

## License

MIT
