---
name: benchmark-verification
description: "Use when changing benchmark tasks, evaluators, test data, or result interpretation for VibeBench. Covers task definitions, expected outputs, and validation against sample inputs."
user-invocable: true
---

# Benchmark Verification

Use this skill when a change can affect whether a generated solution counts as correct.

## When to Use
- Editing `backend/tasks/evaluators.py`
- Updating `test_data/` or task-specific fixtures
- Changing success criteria for task A-H or any output normalization logic

## Procedure
1. Read the task definition, the sample data in `test_data/`, and the relevant evaluator branch.
2. Identify the exact success condition and the failure modes the evaluator is meant to reject.
3. Keep the evaluator deterministic and strict enough to catch incorrect solutions, but avoid false negatives caused by irrelevant formatting differences.
4. If task I/O changes, update the fixtures and any references in the docs or frontend labels.
5. Validate the change against representative sample output, not just by reading code.

## Completion Check
- The evaluator matches the task’s intended behavior.
- Good outputs still pass and obvious failures still fail.
- Any fixture or wording change is reflected in the repo where users will notice it.