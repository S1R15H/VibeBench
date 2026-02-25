# VibeBench Implementation Overview

## Project Summary

VibeBench is a **student research project** designed to evaluate and compare AI-based coding assistants across standardized programming tasks. The goal is to produce a publishable research paper with an open-source framework and public dataset — not a commercial product.

**Timeline:** 12 weeks (one semester)  
**Team:** 4-6 students + 1 faculty advisor  
**Budget:** $0-50 (API trial credits)  
**Stack:** Python + SQLite + Docker (optional)

---

## Requirements Coverage

Every documentation file and implementation component maps to the 5 evaluation factors and 4 report metrics from `REQUIREMENTS.md`:

| Requirement | Factor | Covered By |
|---|---|---|
| Supported programming languages | Factor 1 | `ARCHITECTURE.md` (`language_supported` field), `TEST_DATA_MANAGEMENT.md` (per-task language check), `NICHE_FEATURES.md` (Contribution 8) |
| Bugs and errors in generated code | Factor 2 | `ARCHITECTURE.md` (`compile_status`, `compilation_errors`), `ROADMAP.md` Weeks 3–4 |
| Security vulnerabilities + **mitigation** | Factor 3 | `ARCHITECTURE.md` (`security_issues`, `security_mitigations`, mitigation mapping), `ROADMAP.md` Week 4–5, `NICHE_FEATURES.md` Contribution 3 |
| **Documentation and code readability** | Factor 4 | `ARCHITECTURE.md` (Readability Analyzer section, `readability_score`, `comment_density`), `ROADMAP.md` Week 4–5, `NICHE_FEATURES.md` Contribution 4 |
| Efficiency and performance | Factor 5 | `ARCHITECTURE.md` (`execution_time_ms`, `memory_used_mb`), `ROADMAP.md` Week 3–4 |
| Does code compile without errors? | Req 2.1 | `ARCHITECTURE.md` (`compile_status`), all task verification criteria in `TEST_DATA_MANAGEMENT.md` |
| Does code do what it's supposed to? | Req 2.2 | `ARCHITECTURE.md` (`functional_correctness`), task verifiers in `ROADMAP.md` Week 3–4 |
| **Any warnings when compiled/interpreted?** | Req 2.3 | `ARCHITECTURE.md` (`compilation_warnings` via stderr), `ROADMAP.md` Week 4–5, all task criteria in `TEST_DATA_MANAGEMENT.md` |
| Any security vulnerabilities? | Req 2.4 | `ARCHITECTURE.md` (Bandit/npm audit), `ROADMAP.md` Week 4–5 |
| **Choose best AI per task** (final output) | Core req | `ARCHITECTURE.md` (Best Model Per Task report), `ROADMAP.md` Week 10, `NICHE_FEATURES.md` implicit in all contributions |

---

## Documentation Files

### 1. [REQUIREMENTS.md](REQUIREMENTS.md)
Original project specification + research-focused objectives.
- 8 programming tasks (A–H)
- 5 evaluation factors and 4 report metrics (see table above)
- Research contributions targeting ICSE/FSE/MSR venues
- Explicit list of what is **not** being built (enterprise SaaS, CI/CD, compliance)

### 2. [RESEARCH.md](RESEARCH.md)
Metric definitions and evaluation methodology.
- Factor 1 (Languages): Binary yes/no per task per model
- Factor 2 (Bugs): stderr capture + runtime exception detection; 0/1/2 scoring
- Factor 3 (Security): Bandit, npm audit, SonarQube; High/Medium/Low severity + mitigations
- Factor 4 (Readability): Radon cyclomatic complexity, comment density, Likert scale
- Factor 5 (Performance): `time.perf_counter()`, peak memory

### 3. [GUIDELINES.md](GUIDELINES.md)
Project lifecycle and coding standards.
- Phase A: Framework development (GUI, orchestrator, sandbox, reporting engine)
- Phase B: Experimentation — collect data, automated testing, manual readability review, final report
- Safety: all generated code must run inside Docker; API keys in `.env`

### 4. [ARCHITECTURE.md](ARCHITECTURE.md)
Simple design for a single machine covering all 5 factors.
- **GUI:** Next.js task/model selector
- **Orchestrator:** Fetch → Execute → Capture warnings → Scan security → Analyze readability → Store
- **Database:** SQLite with all required fields (compile_status, compilation_warnings, readability_score, security_mitigations, etc.)
- **Security scanner:** Bandit + mitigation mapping (`B303 → "use bcrypt"`)
- **Readability analyzer:** Radon (cyclomatic complexity) + comment density
- **Report:** Per-run report + final "Best AI Per Task" summary table
- Philosophy: Simple > Complex, Transparent > Black box, Reproducible > Optimized

### 5. [ROADMAP.md](ROADMAP.md)
12-week semester timeline.
- **Phase 1 (Weeks 1–6):** MVP — all 8 tasks working, all 5 metric fields stored, CSV export with warnings + mitigations + readability columns
- **Phase 2 (Weeks 7–9):** Data collection — 320 benchmark runs across 4 models
- **Phase 3 (Weeks 10–12):** Analysis across all 5 factors, Best AI Per Task table, research paper

### 6. [NICHE_FEATURES.md](NICHE_FEATURES.md)
8 research contributions for the paper, each mapping to a requirement:
1. Standardized benchmarking methodology
2. Comparative model evaluation (compilation + correctness)
3. Security analysis + **mitigation suggestions** (Factor 3)
4. **Documentation & readability analysis** using Radon (Factor 4)
5. Model evolution tracking over time
6. Cost-effectiveness analysis
7. Task difficulty analysis
8. **Supported languages & compilation warning patterns** (Factor 1 + Req 2.3)

### 7. [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md)
Local/lab setup in under 15 minutes.
- `git clone` → `npm install` (frontend) & `pip install` (backend) → start dev servers
- Optional Docker for safe code execution
- SQLite only — no database server needed
- API keys in `.env`; cost $0-50 total for whole project

### 8. [TEST_DATA_MANAGEMENT.md](TEST_DATA_MANAGEMENT.md)
Specifications for all 8 benchmark tasks with full verification criteria.
- Each task now has verification criteria covering all 5 factors:
  - **Factor 1** (language support), **Factor 2/Req 2.1** (compile check), **Req 2.3** (warnings), **Req 2.2** (correctness), **Factor 3** (security), **Factor 4** (readability)
- Example CSV captures all 5 factor columns
- Database seeding for Tasks F & G via Docker

### 9. [API_INTEGRATION.md](API_INTEGRATION.md)
Simple 5-minute API setup for 4 models.
- OpenAI GPT-4 Turbo, Anthropic Claude 3 Sonnet, Google Gemini Pro, GitHub Copilot (manual)
- Keys stored in `.env`, loaded with `python-dotenv`
- Simple error handling: 60-second backoff on rate limits

### 10. [INTEGRATION_ROADMAP.md](INTEGRATION_ROADMAP.md)
3 simple optional integrations for research workflow.
1. **GitHub** — public repo for reproducibility
2. **Zenodo/OSF** — permanent dataset archival with DOI
3. **Conference/Journal** — 4–6 page paper (ICSE, FSE, MSR)

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Architecture | Monolithic Python | Simple to understand and debug |
| Database | SQLite | Zero setup, single file, portable |
| Execution | Sequential (not parallel) | Reproducibility > speed |
| Security scanning | Bandit + mitigation mapping | Covers Factor 3 fully including mitigations |
| Readability analysis | Lizard + comment density | Automated Factor 4 metrics across 27+ languages |
| Warning capture | subprocess stderr | Satisfies Requirement 2.3 |
| Final output | Best AI Per Task table | Directly answers core requirement |

---

## Success Criteria

| Week | Milestone |
|------|-----------|
| Week 6 | All 8 tasks execute; all 5 metric columns stored; CSV export with warnings, readability, mitigations |
| Week 9 | 320 benchmark records; Cost within $50; warnings + readability + mitigations logged for all runs |
| Week 12 | Research paper; Best AI Per Task table published; code open-sourced; dataset on Zenodo |

---

## What This Project Is NOT

- ❌ A production SaaS platform
- ❌ An enterprise tool with Kubernetes/multi-region deployment
- ❌ A real-time dashboard with WebSocket streaming
- ❌ A compliance reporting system (SOC2/HIPAA)
- ❌ A 36-week commercial product roadmap

It is a **12-week research project** targeting a conference paper. Simplicity and reproducibility are the top priorities.

---

**Last Updated:** February 2026  
**Status:** All docs aligned with 5 evaluation factors and 4 report metrics from REQUIREMENTS.md
