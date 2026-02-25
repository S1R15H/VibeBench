
# System Architecture (Research Version)

## High-Level Overview
VibeBench is a simple, reproducible benchmarking framework that runs on a single machine (laptop/lab server). The architecture prioritizes clarity, ease of understanding, and reproducibility over scalability.

**Design Philosophy:** 
- Simple > Complex
- Transparent > Black box
- Reproducible > Optimized
- Research-friendly > Enterprise-ready

## Components

### 1. The Frontend (GUI)
* **Tech:** `Next.js` (React framework, modern web GUI)
* **Responsibility:** 
  * User task selection (A-H dropdown)
  * AI model selection (Copilot, GPT-4, Claude, Gemini)
  * "Run Benchmark" button
  * Progress display (current task, AI model)
  * Results summary panel (pass/fail, issue counts)
  * Export button (CSV, JSON)

### 2. The Core Orchestrator & API (Backend)
* **Tech:** `FastAPI` (Python API to connect frontend GUI with the orchestrator)
* **Single-threaded pipeline** (simplicity over performance):
    1. User clicks "Run Benchmark" in Next.js GUI
    2. Frontend sends API request to FastAPI backend
    3. For each AI model (handled by orchestrator):
       - Fetch code (API call or manual input)
       - Save to temporary file
       - Compile/run it
       - Check results
       - Scan for security issues
       - Store results
    4. Return summary to frontend

* **Error handling:** 
    * Timeout: 60 seconds per task
    * Memory limit: Simple subprocess limits
    * Failed task: Log error, continue with next model

### 3. The Sandbox Layer (Docker - Optional)
* **Why Docker?** Safe execution without harming host machine
* **Simple setup:** One Dockerfile with Python + Node.js + PHP
* **Single image:** No complex multi-image strategy
* **Execution:** Each code sample runs in fresh container, then deleted

**Simple Dockerfile:**
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    nodejs npm \
    php \
    mysql-client \
    git
RUN pip install bandit pymongo mysql-connector-python
COPY run_code.py /app/
WORKDIR /app
```

### 4. The Database (SQLite - Single File)
* **Tech:** `SQLite` (no setup needed, single .db file)
* **Schema - Experiments Table:**
  ```
  experiments
  ├─ id (primary key)
  ├─ timestamp (when run)
  ├─ ai_model (Copilot, GPT-4, Claude, Gemini)
  ├─ task_id (A-H)
  ├─ language (python, javascript, php, etc.)
  ├─ language_supported (yes/no — did AI produce a valid file?)
  ├─ code (generated code snippet)
  ├─ compile_status (success/failure/warning)
  ├─ compilation_errors (text from stderr)
  ├─ compilation_warnings (text from stderr — requirement 2.3)
  ├─ functional_correctness (0-1 score — requirement 2.2)
  ├─ security_issues (count — requirement 2.4)
  ├─ security_details (JSON: [{type, severity, line, description}])
  ├─ security_mitigations (JSON: [{issue_id, suggested_fix}])
  ├─ readability_score (integer: Radon cyclomatic complexity)
  ├─ comment_density (float: comment lines / total lines)
  ├─ execution_time_ms (integer)
  ├─ memory_used_mb (integer)
  └─ notes (any observations)
  ```

### 5. Security Scanner (Simple Integration)
* **Python:** `Bandit` — detects injection, hardcoded secrets, weak crypto
* **JavaScript/PHP:** `npm audit` / ESLint security plugin
* **Processing:** Parse output → Extract issue type, severity, line → Store in DB
* **Mitigation output:** For each finding, the framework maps it to a plain-English fix suggestion

**Approach:**
```python
# For each code file
result = subprocess.run(['bandit', '-f', 'json', file], capture_output=True)
issues = parse_bandit_output(result.stdout)

# Map each issue to a mitigation suggestion
MITIGATIONS = {
    'B303': 'Use hashlib.sha256 or bcrypt instead of MD5',
    'B106': 'Remove hardcoded password; use environment variable',
    'B608': 'Use parameterized queries to prevent SQL injection',
    # ... etc.
}
for issue in issues:
    issue['suggested_fix'] = MITIGATIONS.get(issue['test_id'], 'Review and remediate manually')

store_in_database(issues)
```

### 6. Readability Analyzer
* **All languages:** `Lizard` — computes cyclomatic complexity across 27+ languages (Python, JavaScript, PHP, Java, C/C++, Go, Ruby, Rust, Kotlin, Swift, and more)
* **All languages:** Comment density = comment lines / total lines
* **Manual (Phase B):** Likert scale (1–5) for variable naming conventions

```python
import lizard

# Works for any language — just pass the correct file extension
analysis = lizard.analyze_file.analyze_source_code("code.py", source_code)
cyclomatic_score = sum(fn.cyclomatic_complexity for fn in analysis.function_list) / len(analysis.function_list)
comment_density = count_comment_lines(source_code) / total_lines
```

### 7. Cost Tracking (Simple CSV)
* **No complex billing system**
* **Simple tracking:**
  ```csv
  timestamp, ai_model, tokens_input, tokens_output, cost_usd
  2024-02-16T10:30:00, gpt-4, 150, 300, 0.0095
  ```
* **Analysis:** Load CSV into pandas, calculate averages

### 8. Historical Trend Analysis (CSV/JSON)
* **Data storage:** Export results as CSV after each run
* **Analysis:** Python script (matplotlib/seaborn) for trend visualization
* **No real-time dashboard:** Static reports good enough for research

**Trend report example:**
```
gpt-4 Improvement Over Time:
- Week 1: 85% compilation success
- Week 2: 88% compilation success
- Week 3: 90% compilation success
→ Shows clear improvement trend
```

## Data Flow Architecture (Simplified)

```
┌─────────────────────┐
│   User Selects      │
│  Task + AI Model    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  FastAPI     │
    │ Orchestrator │
    └──────┬───────┘
           │
    ┌──────┴──────────┬─────────────┐
    ▼                 ▼             ▼
┌────────────┐  ┌────────────┐  ┌──────────┐
│   Docker   │  │ Bandit/    │  │ Database │
│  Sandbox   │  │ npm audit  │  │ (SQLite) │
│(Execute)   │  │(Scan)      │  │(Store)   │
└────────────┘  └────────────┘  └──────────┘
    │                 │             │
    └─────────────────┴─────────────┘
              │
              ▼
     ┌──────────────────┐
     │ Results Report   │
     │ (CSV/JSON/PDF)   │
     └──────────────────┘
```

## Technology Stack (Research-Friendly)

| Component | Technology | Covers Requirement |
|-----------|-----------|--------------------|
| Language | Python 3.10+ | — |
| GUI | Next.js (React) | Req (1): task selection interface |
| API | FastAPI | Connects Next.js to Python backend |
| Database | SQLite | All metrics stored |
| Code Execution | Docker (optional) | Safe, reproducible, isolated |
| Security Scanning | Bandit, npm audit, ESLint | Factor 3: security vulnerabilities + mitigations; Req 2.4 |
| Readability Analysis | Lizard (cyclomatic complexity, 27+ languages) | Factor 4: documentation & readability |
| Warning Capture | subprocess stderr | Factor 2 + Req 2.3: compilation warnings |
| Analysis | pandas, matplotlib | Summary stats, graphs, best-model ranking |
| Version Control | Git + GitHub | Reproducibility |
| Testing | pytest | Framework correctness |

## Execution Flow (End-to-End Example)

**Scenario:** Student runs Task B (Multi-threaded JSON) on GPT-4

1. **GUI:** Student selects Task B, GPT-4 from dropdowns, clicks "Run"
2. **Fetch Code:** 
   - Call OpenAI API with standard prompt for Task B
   - Receive: Python code with threading
   - Save to: `/tmp/task_b_gpt4_20240216_143022.py`
3. **Execute:**
   - Docker container: `docker run --rm -v /tmp/task_b_gpt4_20240216_143022.py:/code/task.py vibebench python /code/task.py`
   - Input: Sample JSON with 5 records, expect sorted output
   - Output: Verify output matches expected format
4. **Security Scan:**
   - `bandit /tmp/task_b_gpt4_20240216_143022.py`
   - Parse output: 3 issues (hardcoded path, no input validation, missing lock)
5. **Readability:**
   - `lizard task_b_gpt4.py` → cyclomatic complexity score (language auto-detected)
   - Count comment lines → comment density ratio
6. **Store Result:**
   - SQL INSERT: timestamp, model, task, code, compile_status, compilation_warnings, functional_correctness, security_issues, security_mitigations, readability_score, comment_density, execution_time_ms
7. **Display:**
   - GUI shows: "✓ Task B passed (3 security warnings, readability: B)"  
   - User can view generated code, warnings, security mitigations, execution time

## Key Design Decisions

**Single Machine (Laptop/Lab Server)**
- No cloud infrastructure needed
- All code runs locally
- Easy to debug and understand
- Cost: $0 (use existing hardware)

**SQLite Database**
- No separate database server needed
- Single file, easy to backup (`cp experiments.db experiments.db.backup`)
- Easy to export as CSV for analysis
- Query complexity: Simple SELECT/INSERT, no complex joins

**Synchronous Execution**
- Run one benchmark at a time (not parallel)
- Simpler to understand and debug
- Takes longer but no race conditions
- Good for research (reproducibility > speed)

**Docker Optional**
- Can run without Docker for quick testing (use subprocess)
- Docker for final benchmarks (safety, consistency)
- Easy to swap: `docker run` vs `subprocess.run()`

**Manual API Input Option**
- For Copilot (not easily accessible via API)
- Student manually runs prompt in Copilot UI
- Pastes generated code into VibeBench
- No fancy API automation needed

**CSV Export for Analysis**
- Export results from SQLite to CSV
- Use standard tools (Excel, Python, R) for analysis
- No custom dashboards needed
- Transparent: Anyone can analyze the data

**Best Model Per Task Report**
- After collecting all benchmark data, generate a summary table:

  ```
  Task | Best Compilation | Best Security | Best Readability | Best Overall
  A    | GPT-4 (98%)      | Claude (0.8 avg) | Gemini (CC=2)  | GPT-4
  B    | Claude (91%)     | Claude (1.1 avg) | GPT-4 (CC=3)   | Claude
  ...
  ```
- This is the final required output: "choose the best AI-based Coding Assistant tool for each programming task"

## Deployment on Lab Server

**Minimal Setup (< 30 minutes):**
```bash
# On lab server (Ubuntu 22.04)
git clone https://github.com/S1R15H/VibeBench.git
cd VibeBench/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the Python Backend API
uvicorn api:app --reload &

# Start the Next.js Frontend
cd ../frontend
npm install
npm run dev

# Or run from command line without GUI
cd ../backend
python cli.py --model gpt-4 --task B --language python
```

**No complex infrastructure:**
- ❌ Kubernetes
- ❌ Multiple databases
- ❌ Load balancing
- ❌ Multi-region replication
- ✅ Just Python + Docker + SQLite

## Reproducibility

**For other researchers to reproduce results:**
1. Download VibeBench code from GitHub
2. Setup same Docker image (Dockerfile included)
3. Use same test data (`test_data/` folder)
4. Run same prompts (documented in PROMPTS.md)
5. Get same results (or close, given model non-determinism)

**Reproducibility documentation:**
- Exact Python version used: `3.10.12`
- Exact model versions: `gpt-4-turbo-2024-04-09`, etc.
- Exact test data: Versioned in git
- Random seeds: Fixed for deterministic runs where applicable
- Timestamp: Every benchmark run is timestamped

## What's NOT in This Architecture

**Deliberately omitted for simplicity:**
- ❌ Real-time WebSocket dashboard (CSV reports sufficient)
- ❌ Multi-region deployment (single lab server)
- ❌ Advanced time-series database (SQLite is fine)
- ❌ Elasticsearch indexing (not needed for 1000s of records)
- ❌ Auto-scaling (manual upscaling via bigger server if needed)
- ❌ Microservices (monolithic = simpler)
- ❌ API gateway (direct script/GUI calls)
- ❌ Distributed job queue (sequential execution)

This keeps the codebase small (~2000 lines Python), understandable, and easy for students to modify for their research.

