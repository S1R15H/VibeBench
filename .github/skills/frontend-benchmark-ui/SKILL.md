---
name: frontend-benchmark-ui
description: "Use when editing the VibeBench Next.js frontend, including dashboard, run, and history pages, shared components, layout, styling, and API wiring to the backend."
user-invocable: true
---

# Frontend Benchmark UI

Use this skill for changes under `frontend/src/app/` and related UI styling.

## When to Use
- Editing the dashboard, run flow, history table, navbar, or shared UI components
- Adjusting backend fetch calls, loading states, or result rendering
- Refreshing Tailwind styling, layout, or visual hierarchy in the app shell

## Procedure
1. Inspect the target page or component and confirm which backend endpoint it consumes.
2. Keep the run flow aligned with the backend contract: benchmark submission, results fetch, and status display.
3. Preserve or intentionally redesign the visual language consistently across `page.tsx`, shared components, and `globals.css`.
4. Make loading, empty, and error states explicit; do not leave a screen dependent on hidden assumptions about backend availability.
5. Keep the UI responsive and accessible: readable table states, clear button hierarchy, and predictable navigation.
6. After editing, run the narrowest relevant frontend validation, usually lint plus a build check for the touched area.

## Completion Check
- The page still renders cleanly on desktop and mobile.
- API calls still point at the correct backend routes.
- Empty-state and failure behavior are still visible and understandable.