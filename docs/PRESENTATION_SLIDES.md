# VibeBench Project Presentation (PowerPoint-Ready)

Use this file as a slide-by-slide script for your presentation. Each section below maps to your grading rubric.

## Slide 1 - Project Title (2 pts)

**Title:** VibeBench: A Comparative Benchmarking Framework for AI Coding Assistants  
**Course/Section:** [Add course and section]  
**Team Members:** [First Last], [First Last], [First Last], [First Last]  
**Date:** April 2026

Suggested visual: VibeBench logo/title with a simple subtitle: "8 tasks, 5 quality factors, reproducible evaluation".

---

## Slide 2 - Abstract (5 pts)

VibeBench is a research-focused software framework that evaluates and compares AI coding assistants on standardized software engineering tasks. Our objective was to build a reproducible system that measures generated-code quality using five factors: language support, bugs/errors, security vulnerabilities with mitigations, readability/documentation quality, and efficiency/performance. The solution combines a Next.js frontend, a FastAPI orchestration backend, static-analysis integrations, and SQLite-based experiment logging. We implemented an end-to-end benchmark pipeline for tasks A-H (file I/O, concurrency, archiving, relational/non-relational data access, and authentication logic), plus exportable results for historical analysis and reporting.

**Keywords:** AI coding assistants, software benchmarking, static analysis, reproducibility, code quality

---

## Slide 3 - Problem Statement (8 pts)

AI coding assistants can generate code quickly, but teams often lack an objective and reproducible way to compare them across realistic programming tasks and quality dimensions.

Our project solves this by providing a benchmark framework that:
- Tests multiple AI models on the same task definitions.
- Measures correctness, security, readability, warnings/errors, and runtime efficiency.
- Stores all outcomes in a structured dataset to identify the best model per task.

---

## Slide 4 - Core Design Overview (25 pts)

**Design goal:** transparent, research-friendly, locally reproducible benchmarking.

**Pipeline:**
1. User selects task, model, and language in the frontend.
2. FastAPI endpoint receives benchmark request.
3. Orchestrator generates/accepts code, writes temp file, executes with task fixtures.
4. Evaluators compute correctness and quality-gate status.
5. Scanners compute security/readability metrics.
6. Results are persisted in SQLite and shown in dashboard/history views.

**Why this design:** easy to debug, easy to extend, and aligned with research reproducibility.

---

## Slide 5 - Tech Stack, Tools, and Versions (25 pts)

**Languages and Frameworks**
- Python 3.14.0 (project requirement: Python 3.10+)
- FastAPI (backend API), Uvicorn 0.38.0
- TypeScript + Next.js 16.2.4 frontend
- React 19.2.3, Tailwind CSS 4, ESLint 9.38.0

**DBMS**
- SQLite 3.51.0 (`experiments.db`)

**Static Analysis and Quality Tools**
- Bandit 1.8.6 (Python security)
- Semgrep 1.161.0 (cross-language security patterns)
- ShellCheck (Bash checks, if installed)
- Radon 6.0.1 (Python complexity)
- Lizard 1.22.1 (multi-language complexity)

**Execution Environment**
- OS: macOS 26.3.1 (Darwin)
- Node.js 22.19.0, npm 10.9.3

---

## Slide 6 - System Architecture Diagram (25 pts)

Copy this diagram into PowerPoint as SmartArt or redraw with shapes:

```text
+----------------------+         +-------------------------+
| Next.js Frontend     |  HTTP   | FastAPI Backend         |
| - Task/model select  +-------->+ /api/benchmark          |
| - Run dashboard      |         | /api/results            |
| - History/Export     |         | /api/export/csv         |
+----------+-----------+         +-----------+-------------+
           |                                 |
           |                                 v
           |                      +----------+-------------+
           |                      | Experiment Orchestrator |
           |                      | - Generate/load code    |
           |                      | - Execute in runtime    |
           |                      | - Evaluate correctness  |
           |                      +----+-----------+--------+
           |                           |           |
           |                           |           |
           |                           v           v
           |                  +--------+--+   +----+----------------+
           |                  | Scanners  |   | SQLite experiments  |
           |                  | Bandit    |   | - metrics           |
           |                  | Semgrep   |   | - code/output       |
           |                  | Radon     |   | - notes/metadata    |
           |                  | Lizard    |   +---------------------+
           |                  +-----------+
```

---

## Slide 7 - UML Statechart (Benchmark Run Lifecycle)

```text
[Idle]
  -> (User selects task/model/language) -> [Configured]
[Configured]
  -> (Run clicked) -> [Generating_or_Loading_Code]
[Generating_or_Loading_Code]
  -> (Code available) -> [Executing]
  -> (Generation failed) -> [Failed]
[Executing]
  -> (Timeout/runtime error) -> [Failed]
  -> (Execution complete) -> [Evaluating]
[Evaluating]
  -> (Scans + scoring complete) -> [Persisting_Result]
[Persisting_Result]
  -> (DB write success) -> [Completed]
  -> (DB write error) -> [Failed]
[Completed]
  -> (User runs again) -> [Configured]
[Failed]
  -> (User retries) -> [Configured]
```

---

## Slide 8 - ER Diagram (SQLite Schema)

```text
+---------------------------------------------------------------+
| experiments                                                   |
+---------------------------------------------------------------+
| PK id : INTEGER                                               |
| timestamp : TEXT                                              |
| ai_model : TEXT                                               |
| model_id : TEXT                                               |
| model_region : TEXT                                           |
| task_id : TEXT                                                |
| language : TEXT                                               |
| language_supported : TEXT                                     |
| code : TEXT                                                   |
| compile_status : TEXT                                         |
| compilation_errors : TEXT                                     |
| compilation_warnings : TEXT                                   |
| execution_output : TEXT (JSON payload)                        |
| functional_correctness : REAL                                 |
| security_issues : INTEGER                                     |
| security_details : TEXT (JSON array)                          |
| security_mitigations : TEXT (JSON array)                      |
| readability_score : REAL                                      |
| comment_density : REAL                                        |
| execution_time_ms : INTEGER                                   |
| memory_used_mb : INTEGER                                      |
| notes : TEXT (quality-gate and score metadata)                |
+---------------------------------------------------------------+
```

Note: Current implementation stores all benchmark facts in one denormalized table for reproducibility and easy CSV export.

---

## Slide 9 - Similar Products and Methodologies (Core Design)

**Comparable benchmarks/methodologies**
- HumanEval/MBPP style code-generation benchmarking (correctness-centric).
- SWE-Bench style software task evaluation (issue/task-oriented workflow).
- OWASP/CWE-aligned static analysis methodologies for vulnerability classification.

**How VibeBench differs**
- Integrates correctness + security + readability + warnings + runtime metrics in one pipeline.
- Uses standardized, task-specific fixtures (A-H) and persistent local experiment logs.
- Targets educational/research reproducibility over enterprise-scale deployment.

---

## Slide 10 - Evaluation Method (25 pts)

We evaluated the framework using deterministic task fixtures in `test_data/` and automated checks in evaluators/scanners.

**Success criteria per run**
- Compile/interpret status is not failure.
- Functional correctness for the selected task is verified.
- Security findings are detected and mitigations are suggested.
- Readability metrics are computed (complexity + comment density).
- Runtime is measured and stored.

**Evidence source**
- API outputs and persisted records in SQLite (`experiments` table).
- Dashboard and history page visual summaries.

---

## Slide 11 - Use Case 1 (Evaluation)

**Use Case:** Run Task A (Read text file and compute aggregates)

**Actor:** Student researcher  
**Precondition:** Backend and frontend running; task fixture exists in `test_data/task_a/input.txt`.  
**Main flow:**
1. User selects Task A, model, and language.
2. System runs benchmark pipeline and computes output.
3. Evaluator compares execution output against expected JSON structure.
4. Scanner tools add security/readability metrics.
5. Result is saved and shown in UI.

**Outcome:** User receives compile status, correctness score, security issues, readability score, and execution time for that run.

---

## Slide 12 - Use Case 2 (Evaluation)

**Use Case:** Run Task H (Password-based authentication utility)

**Actor:** Student researcher  
**Precondition:** Task H test input exists in `test_data/task_h/auth_input.json`.  
**Main flow:**
1. User runs Task H for selected model.
2. Generated code executes and returns hashed/authentication-related output.
3. Evaluator verifies expected token/hash pattern.
4. Security scanner flags weak primitives or unsafe patterns if present.
5. Result and mitigation advice are stored.

**Outcome:** Security posture and correctness can be compared across AI models for an auth-sensitive task.

---

## Slide 13 - Test Cases and Results (Required format)

Use this slide as a table. Replace "Observed Result" with your actual run output.

| Test Case ID | Brief Description | SRS Requirement | Environment | Observed Result | Verdict |
|---|---|---|---|---|---|
| TC-01 | Health/API availability check (`GET /api/health`) | GUI + reporting readiness | macOS 26.3.1, Python 3.14.0, Uvicorn 0.38.0 | Backend returned `status=ok`; DB reachable | Pass |
| TC-02 | Task A benchmark run validates expected aggregates | (2.1) compile/interpret status, (2.2) correctness, Factor 5 runtime | macOS 26.3.1, Node 22.19.0, SQLite 3.51.0 | Compile status captured; correctness evaluated against expected output; runtime stored | Pass |
| TC-03 | Warning capture on interpreted run | (2.3) warnings during compile/interpret | Same as TC-02 | `stderr` persisted into `compilation_warnings` when non-fatal warnings appear | Pass |
| TC-04 | Security scanning and mitigation mapping | (2.4) vulnerabilities + Factor 3 mitigation | Bandit 1.8.6, Semgrep 1.161.0 | Findings counted in `security_issues`; details and mitigations saved | Pass |
| TC-05 | Readability metric computation | Factor 4 documentation/readability | Radon 6.0.1, Lizard 1.22.1 | `readability_score` and `comment_density` stored in DB | Pass |
| TC-06 | CSV export of benchmark history (`GET /api/export/csv`) | Report generation requirement | FastAPI + SQLite environment | CSV downloaded with experiment columns | Pass |

---

## Slide 14 - Accomplishments and Conclusion

**What we accomplished**
- Built an end-to-end benchmark platform (frontend + backend + persistence).
- Implemented 8 standardized task categories (A-H) aligned to project requirements.
- Integrated security and readability analysis into each benchmark run.
- Added experiment history and CSV export for reproducible analysis.
- Created a foundation to determine best AI assistant per task.

**Conclusion**
VibeBench provides a practical, research-oriented framework for objective comparison of AI coding assistants under consistent task and quality constraints.

---

## Slide 15 - Future Work (Optional)

- Add automated multi-model batch runs and statistical significance analysis.
- Expand vulnerability mapping to CWE/OWASP categories in reports.
- Add richer trend analytics and per-task winner visualizations.
- Containerize execution path by default for stronger isolation.

---

## Presenter Notes

- Keep Slide 2 under 60-90 seconds.
- Spend most time on Slides 4-13 (core design + evaluation carries highest points).
- Bring one screenshot each from Run page and History page to strengthen evidence.
- If asked about limitations: mention local single-machine design and denormalized schema choices made for reproducibility and simplicity.
