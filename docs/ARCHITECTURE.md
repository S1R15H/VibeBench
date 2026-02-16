
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
* **Tech:** Python `PyQt6` (lightweight, single executable)
* **Responsibility:** 
  * User task selection (A-H dropdown)
  * AI model selection (Copilot, GPT-4, Claude, Gemini)
  * "Run Benchmark" button
  * Progress display (current task, AI model)
  * Results summary panel (pass/fail, issue counts)
  * Export button (CSV, JSON)

### 2. The Core Orchestrator (Backend)
* **Single-threaded pipeline** (simplicity over performance):
    1. User clicks "Run Benchmark"
    2. For each AI model:
       - Fetch code (API call or manual input)
       - Save to temporary file
       - Compile/run it
       - Check results
       - Scan for security issues
       - Store results
    3. Display summary

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
* **Schema - Simple Experiments Table:**
  ```
  experiments
  ├─ id (primary key)
  ├─ timestamp (when run)
  ├─ ai_model (Copilot, GPT-4, Claude, Gemini)
  ├─ task_id (A-H)
  ├─ language (python, javascript, etc)
  ├─ code (generated code snippet)
  ├─ compile_status (success/failure)
  ├─ compilation_errors (text)
  ├─ functional_correctness (0-1 score)
  ├─ security_issues (count)
  ├─ security_details (JSON)
  ├─ execution_time_ms (integer)
  ├─ memory_used_mb (integer)
  └─ notes (any observations)
  ```

### 5. Security Scanner (Simple Integration)
* **Python:** Bandit (already available, single command)
* **JavaScript:** npm audit (built-in)
* **PHP:** PHPStan (installed in Docker)
* **Processing:** Parse output → Extract issues → Store in DB

**Simple approach:**
```python
# For each code file
result = subprocess.run(['bandit', file], capture_output=True)
issues = parse_bandit_output(result.stdout)
store_in_database(issues)
```

### 6. Cost Tracking (Simple CSV)
* **No complex billing system**
* **Simple tracking:**
  ```csv
  timestamp, ai_model, tokens_input, tokens_output, cost_usd
  2024-02-16T10:30:00, gpt-4, 150, 300, 0.0095
  ```
* **Analysis:** Load CSV into pandas, calculate averages

### 7. Historical Trend Analysis (CSV/JSON)
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
    │ Orchestrator │
    │  (Python)    │
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

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.10+ | Easy to read, widely used in research |
| GUI | PyQt6 | Simple, no build step needed |
| Database | SQLite | Zero setup, single file, portable |
| Code Execution | Docker | Safe, reproducible, isolated |
| Security Scanning | Bandit, npm audit | Free, well-known, easy to parse |
| Analysis | pandas, matplotlib | Standard for data analysis |
| Version Control | Git + GitHub | Transparent, public code |
| Testing | pytest | Simple unit tests for verifying tasks |

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
5. **Store Result:**
   - SQL INSERT: timestamp, model, task, code, success, issues_count, issues_json
6. **Display:**
   - GUI shows: "✓ Task B passed (3 security warnings)"
   - User can view generated code, issues, execution time

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

## Deployment on Lab Server

**Minimal Setup (< 30 minutes):**
```bash
# On lab server (Ubuntu 22.04)
git clone https://github.com/S1R15H/VibeBench.git
cd VibeBench
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: Setup Docker for safe execution
docker build -t vibebench .

# Run the GUI
python src/gui.py

# Or run from command line
python src/cli.py --model gpt-4 --task B --language python
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

