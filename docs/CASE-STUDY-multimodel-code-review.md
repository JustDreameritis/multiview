# Case Study: 6-Model AI Code Review — 19 Issues Found

## Problem Statement

Code review is expensive. Human reviewers miss issues, get fatigued, and can't cover all angles (security, performance, architecture) equally well. Existing AI code review tools use single models, missing consensus opportunities. The goal:

- Parallel review from 6 specialist AI models
- Each model focuses on a specific domain (security, performance, edge cases, etc.)
- Deduplicate findings across models (similar issues shouldn't appear 6 times)
- Rank by severity with model consensus tracking
- Zero cost — use free API tiers only

## Technical Approach

### Multi-Model Architecture
```
Code Input → 6 Parallel API Calls → Finding Collection → Deduplication → Ranking → Output
                    ↓
    [Security] [Architecture] [Performance] [Edge Cases] [Deep Reasoning] [Quality]
```

### Specialist Reviewers
| Model | Provider | Specialty | Focus |
|-------|----------|-----------|-------|
| Llama 4 Scout | Groq | Security | XSS, injection, auth flaws |
| Gemma 2 9B | Groq | Architecture | SOLID, coupling, patterns |
| Mistral Small | Mistral | Performance | Time complexity, memory, I/O |
| Gemini 2.0 Flash | Google | Edge Cases | Null handling, bounds, race conditions |
| DeepSeek R1 | DeepSeek | Deep Reasoning | Complex logic, state machines |
| Qwen 32B | OpenRouter | Code Quality | Style, naming, documentation |

### Deduplication Algorithm
1. Normalize finding titles (lowercase, remove punctuation)
2. Extract key phrases from descriptions
3. Fuzzy match with 80% similarity threshold
4. Group similar findings, keep highest-severity instance
5. Track which models found each issue (consensus count)

### Output Formats
- **Terminal** — Rich colored table with severity highlighting
- **JSON** — Structured output for CI/CD pipelines
- **Markdown** — PR comment ready with expandable sections

## Stack Used

| Category | Technologies |
|----------|-------------|
| Language | Python 3.9+ |
| HTTP | async httpx |
| CLI | Click |
| Output | Rich (tables, colors) |
| Fuzzy Matching | RapidFuzz |
| APIs | Groq, Mistral, Google AI, DeepSeek, OpenRouter |

## Key Metrics

| Metric | Value |
|--------|-------|
| Total code lines | 1,356 |
| Specialist models | 6 |
| API cost | $0 (free tiers) |
| Parallel execution | Yes (async) |
| Average review time | 15-30 seconds |
| Issues found (fleet codebase) | 19 |
| Deduplication rate | ~40% (6 models → unique findings) |

### Issues Found in Production Code
When run against the trading fleet codebase:
- 4 CRITICAL (unhandled exceptions in order execution)
- 6 HIGH (race conditions, missing validation)
- 7 MEDIUM (error handling gaps, logging issues)
- 2 LOW (naming conventions, documentation)

All 4 CRITICAL issues were fixed before production deployment.

## Challenges Overcome

### 1. Model Output Inconsistency
**Issue:** Each model returns findings in different formats (some use markdown, some plain text, severity naming varies).
**Solution:** Wrote model-specific parsers that normalize output to common Finding schema. Fuzzy severity mapping (e.g., "SEVERE" → "CRITICAL").

### 2. Rate Limiting
**Issue:** Free API tiers have strict rate limits. 6 parallel calls can hit limits.
**Solution:** Implemented per-provider rate limiting with exponential backoff. Stagger requests slightly (50ms between providers).

### 3. Finding Overlap
**Issue:** Same issue detected by 4 models creates noise.
**Solution:** Fuzzy deduplication with 80% threshold. Consensus tracking shows "Found by: 4/6 models" — higher consensus = higher confidence.

## GitHub Repository

[github.com/JustDreameritis/multiview](https://github.com/JustDreameritis/multiview)

**Installation:**
```bash
pip install multiview
```

**Usage:**
```bash
multiview review app.py
multiview review src/ --format json
multiview review . --format markdown > review.md
```

## Lessons Learned

1. **Specialists beat generalists** — 6 focused models find more than 1 large model trying to cover everything. Domain expertise matters.

2. **Consensus builds confidence** — If 5/6 models flag the same issue, it's almost certainly real. Single-model findings need more scrutiny.

3. **Free tiers are sufficient** — $0 API cost for production-quality code review. Free tiers have enough quota for regular development use.

4. **Deduplication is critical** — Without it, 6 models = 6x noise. Smart deduplication makes multi-model practical.

5. **CI/CD integration is table stakes** — JSON output for automated pipelines. Block PRs on CRITICAL findings.

---

*Demonstrates multi-model AI orchestration for practical developer tooling, achieving better results than single-model approaches at zero cost.*
