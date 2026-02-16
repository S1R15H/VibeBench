# Research & Evaluation Strategy

## 1. Metric Definitions

### A. Supported Languages
* **Measurement:** Binary (Yes/No) per task.
* **Validation:** Can the AI generate a valid file extension for the requested task?

### B. Bugs and Errors
* **Compile-Time:** Capture `stderr` from the compiler (javac, gcc) or interpreter (python).
* **Runtime:** Catch Exceptions/Errors during execution.
* **Scoring:** 0 = Critical Failure, 1 = Runs with Warnings, 2 = Perfect Run.

### C. Security Vulnerabilities
* **Tooling:**
    * **Python:** `Bandit` (focus on `exec`, `eval`, hardcoded SQL).
    * **JS/PHP:** `SonarQube` (Community Edition) or `npm audit` / `rips`.
    * **C/C++:** `CppCheck`.
* **Metric:** Count of "High", "Medium", and "Low" severity issues.

### D. Documentation & Readability
* **Automated Metric:** **Cyclomatic Complexity** (using `Radon` for Python). Lower is better.
* **Automated Metric:** **Comment Density** (Ratio of comment lines to code lines).
* **Human Metric:** Likert scale (1-5) on variable naming conventions.

### E. Efficiency
* **Time:** `time.perf_counter()` start vs end.
* **Resource:** Peak memory usage during execution.

## 2. The 8 Tasks: Implementation Details

* **Task (b) & (d) Multithreading:**
    * *Check:* The framework must verify that threads were actually used (e.g., checking active thread count during execution or inspecting imports).
* **Task (f) & (g) Databases:**
    * *Strategy:* The Docker environment must have a pre-seeded MySQL and MongoDB instance running so the generated code has something to connect to.
    * *Success:* The code retrieves the specific record "SampleRecord_123".
* **Task (h) Auth:**
    * *Security Check:* Does it hash the password? If it stores plain text, it fails the security metric immediately.