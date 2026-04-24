---
name: backend-benchmark-change
description: "Use when editing VibeBench backend FastAPI routes, the orchestrator, SQLite persistence, task evaluators, or security/readability scanners. Covers request flow, temp-file execution, database schema, and benchmark-result contracts."
user-invocable: true
---

# Backend Benchmark Change

Use this skill for changes in `backend/` that affect the API, execution pipeline, scanners, or result storage.

## When to Use
- Editing `backend/api.py`, `backend/orchestrator.py`, `backend/database.py`, `backend/tasks/`, or `backend/scanners/`
- Changing benchmark request/response shapes or result fields
- Updating task evaluation logic, language support, or scan behavior

## Procedure
1. Read the relevant backend file and the project context in `docs/ARCHITECTURE.md` and `docs/GUIDELINES.md`.
2. Trace the request path end to end: API request -> orchestrator -> task execution -> scanners -> database write.
3. Preserve public contracts unless the change explicitly requires a breaking update: supported languages, task IDs A-H, and stored result fields.
4. Keep execution changes safe and local: timeout handling, temp-file cleanup, and task-specific working directories should remain intact.
5. If changing evaluator or scanner behavior, update the corresponding task data or mitigation mapping so result interpretation stays consistent.
6. After editing, run the narrowest useful validation for the touched slice, such as backend linting, module compilation, or a focused smoke test.

## Completion Check
- The backend still returns the expected result structure.
- SQLite writes still succeed with the current schema.
- The change does not weaken error handling, timeout behavior, or cleanup.