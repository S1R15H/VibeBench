### Context
- [ ] **FE-CONTEXT-1.1 Framework**: Next.js 16.2.4 with React 19.2.3 and TypeScript 5.
- [ ] **FE-CONTEXT-1.2 Design Source**: Written requirement from user report in history graphs (average security issues graph missing, zeros must be included).
- [ ] **FE-CONTEXT-1.3 Budgets/Standards**: Preserve existing app behavior, keep dashboard/history responsive, and maintain WCAG 2.1 AA-friendly states.

### Implementation Plan
- [ ] **FE-PLAN-1.1 Fix zero-safe metric aggregation**:
	- **Scope**: Remove non-zero filtering from model-average calculations so `0` values are counted.
	- **Components**: `frontend/src/app/history/page.tsx`
	- **State**: No new state; update `useMemo` aggregation logic only.
	- **Responsive**: No layout changes, preserve current responsive grid.
- [ ] **FE-PLAN-1.2 Fix graph visibility for all-zero datasets**:
	- **Scope**: Ensure bar sections still render rows when values are zero.
	- **Components**: `frontend/src/app/history/page.tsx`
	- **State**: No additional state.
	- **Responsive**: Maintain existing card/table layout from mobile to desktop.
- [ ] **FE-PLAN-1.3 Align copy and value formatting**:
	- **Scope**: Update metric text and numeric formatting so zero values display as `0.00`/`0.0%` instead of `-`.
	- **Components**: `frontend/src/app/history/page.tsx`
	- **State**: None.
	- **Responsive**: N/A (text-only adjustments).

### Implementation Items
- [ ] **FE-ITEM-1.1 BenchmarkResult metric typing hardening**:
	- **Props**: Allow nullable numeric metrics from API rows (`functional_correctness`, `security_issues`, `readability_score`).
	- **State**: Existing `results` state remains unchanged.
	- **Accessibility**: Preserve existing semantic sections and readable fallback text.
	- **Performance**: O(1) helper checks and existing O(n) aggregation preserved.
- [ ] **FE-ITEM-1.2 Zero-inclusive averages per model**:
	- **Props**: No prop changes.
	- **State**: No state changes.
	- **Accessibility**: Keeps graph labels visible for screen magnification users even when bar widths are 0.
	- **Performance**: Single-pass aggregate loop remains unchanged in complexity.
- [ ] **FE-ITEM-1.3 Graph rendering and formatter fixes**:
	- **Props**: `renderMetricBars` uses existing signature.
	- **State**: No state changes.
	- **Accessibility**: Empty-state language changed to reflect missing data, not non-zero filtering.
	- **Performance**: No measurable bundle/runtime impact.

### Proposed Code Changes
```diff
*** Begin Patch
*** Update File: /Users/sirishgurung/Desktop/VibeBench/VibeBench/frontend/src/app/history/page.tsx
@@
 type BenchmarkResult = {
   id: number;
   ai_model: string;
   model_id?: string;
   task_id: string;
   compile_status: string;
-  functional_correctness: number;
-  security_issues: number;
-  readability_score: number;
+  functional_correctness: number | null;
+  security_issues: number | null;
+  readability_score: number | null;
   code?: string;
   execution_output?: string | Record<string, unknown>;
 };
@@
 export default function HistoryPage() {
   const [results, setResults] = useState<BenchmarkResult[]>([]);
   const [status, setStatus] = useState("Loading history...");
+
+  const isFiniteMetric = (value: number | null | undefined): value is number =>
+    typeof value === "number" && Number.isFinite(value);
@@
-      if (run.readability_score > 0) {
+      if (isFiniteMetric(run.readability_score)) {
         aggregates.readability.sum += run.readability_score;
         aggregates.readability.count += 1;
       }
 
-      if (run.security_issues > 0) {
+      if (isFiniteMetric(run.security_issues)) {
         aggregates.security.sum += run.security_issues;
         aggregates.security.count += 1;
       }
 
-      if (run.functional_correctness > 0) {
+      if (isFiniteMetric(run.functional_correctness)) {
         aggregates.correctness.sum += run.functional_correctness;
         aggregates.correctness.count += 1;
       }
@@
-    const hasValues = modelAverages.some((item) => item[metric] > 0);
+    const hasValues = modelAverages.length > 0;
@@
-            <p className="text-sm text-neutral-500">No non-zero values available for this metric yet.</p>
+            <p className="text-sm text-neutral-500">No values available for this metric yet.</p>
@@
-              const width = value > 0 ? Math.min((value / maxValue) * 100, 100) : 0;
+              const width = Math.max(0, Math.min((value / maxValue) * 100, 100));
@@
             <h2 className="text-2xl font-bold">Model Average Metrics</h2>
             <p className="text-neutral-400 mt-2">
-              Bar graphs by model using non-zero values only for average readability, security, and correctness.
+              Bar graphs by model for average readability, security issues, and correctness (including zero values).
             </p>
           </div>
@@
               "Average Readability",
               "readability",
               metricMax.readability,
               "bg-emerald-500",
-              (value) => (value > 0 ? value.toFixed(2) : "-")
+              (value) => value.toFixed(2)
             )}
             {renderMetricBars(
               "Average Security Issues",
               "security",
               metricMax.security,
               "bg-rose-500",
-              (value) => (value > 0 ? value.toFixed(2) : "-")
+              (value) => value.toFixed(2)
             )}
             {renderMetricBars(
               "Average Correctness",
               "correctness",
               metricMax.correctness,
               "bg-sky-500",
-              (value) => (value > 0 ? `${(value * 100).toFixed(1)}%` : "-")
+              (value) => `${(value * 100).toFixed(1)}%`
             )}
*** End Patch
```

### Commands
- [ ] **FE-CMD-1.1 Local lint**: `cd frontend && npm run lint`
- [ ] **FE-CMD-1.2 Local build check**: `cd frontend && npm run build`
- [ ] **FE-CMD-1.3 Backend smoke (optional for contract check)**: `cd backend && source .venv/bin/activate && python -m uvicorn api:app --reload`

## Quality Assurance Task Checklist
- [ ] **FE-QA-1.1** All components compile without TypeScript errors
- [ ] **FE-QA-1.2** Responsive design tested at 320px, 768px, 1024px, 1440px, and 2560px
- [ ] **FE-QA-1.3** Keyboard navigation reaches all interactive elements
- [ ] **FE-QA-1.4** Color contrast meets WCAG AA minimums verified with tooling
- [ ] **FE-QA-1.5** Core Web Vitals pass Lighthouse audit with scores above 90
- [ ] **FE-QA-1.6** Bundle size impact measured and within performance budget
- [ ] **FE-QA-1.7** Cross-browser testing completed on Chrome, Firefox, Safari, and Edge
