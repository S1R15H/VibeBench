
# System Architecture

## High-Level Overview
The software uses a **Controller-Agent** pattern with a layered architecture supporting real-time analysis, historical tracking, and multi-dimensional quality evaluation. The "Controller" (GUI/API) directs specific "Agents" (Runners) to process code snippets through modular analysis pipeline.

## Components

### 1. The Frontend (GUI & Dashboard)
* **Tech:** 
  * Primary: Python `PyQt6` for desktop UI
  * Secondary: React/Vue.js for real-time web dashboard
* **Responsibility:** 
  * User input, task selection, AI model selection
  * Real-time progress monitoring with WebSocket streaming
  * Result visualization (comparative charts, trend graphs)
  * Historical data browsing and filtering

### 2. The Orchestrator (Backend Logic & Pipeline Manager)
* **Core Pipeline:**
    1.  Receives source code string + language + task ID + AI model metadata
    2.  Saves code to temporary file with metadata tracking
    3.  Triggers the **Compiler/Interpreter** with timeout enforcement
    4.  Triggers the **Test Runner** (injects input data, checks output, measures performance)
    5.  Triggers the **Security Scanner Suite** (parallel execution)
    6.  Triggers the **Compliance Analyzer** (OWASP, regulatory checks)
    7.  Aggregates results into JSON object and stores in time-series database
    8.  Streams results via WebSocket to real-time dashboard

* **Error Recovery:**
    * Timeout handlers (configurable per task/language)
    * Memory limit enforcement with OOM detection
    * Hanging process termination with cleanup
    * Graceful degradation for partial analysis failures

### 3. The Sandbox Layer (Docker Orchestration)
* **Ephemeral Container Strategy:** Each code execution in isolated, resource-limited container
* **Image A (Python Base):** Python 3.10+, Pandas, MySQL/MongoDB connectors, Bandit (security)
* **Image B (Web Base):** Node.js, PHP, Apache, ESLint, npm audit
* **Image C (Compiled Languages):** GCC, Java, CppCheck, SonarQube scanner
* **Resource Limits:** CPU limits (1-2 cores), memory limits (512MB-1GB), disk quotas, network isolation
* **Network Policy:** No external outbound; all I/O through mounts; database access via localhost bridge

### 4. The Database Layer
* **Primary DB: SQLite** (for framework data and experiment metadata)
  * Schema: `Experiments` table (ID, Timestamp, AI_Name, Model_Version, Task_ID, Language, Code_Snippet, Compile_Status, Functional_Correctness, Warning_Count, Security_Vulnerabilities, Performance_Metrics)
  
* **Time-Series DB: InfluxDB/Prometheus** (for historical trend tracking)
  * Stores aggregated metrics per model/task/language for fast time-series queries
  * Enables trend analysis and model improvement tracking over weeks/months
  * Supports distributed writes for horizontal scaling

* **Search Index: Elasticsearch** (optional for large-scale deployments)
  * Full-text search of generated code snippets and findings
  * Aggregation queries for compliance reporting

### 5. Security Scanner Suite (Modular)
* **Python:** Bandit (security vulnerabilities), Pylint (code quality)
* **JavaScript/Node.js:** ESLint, npm audit, OWASP Dependency Check
* **PHP:** PHPStan, PHPCS, npm audit (if using packages)
* **C/C++:** CppCheck, Flawfinder, Address Sanitizer (ASan)
* **Java:** SpotBugs, FindBugs, OWASP Dependency Check
* **Generic:** SonarQube integration for cross-language analysis

* **Output Processing:** Regex parsers to extract severity, line numbers, vulnerability types from each tool's output

### 6. Compliance & Regulatory Analysis Module (Tier 2+)
* **OWASP Mapping:** Classify findings against OWASP Top 10 categories
* **CVE Database Integration:** Match detected vulnerabilities to known CVE records
* **Compliance Checkers:** SOC2, HIPAA, PCI-DSS alignment verification
* **Report Generator:** Audit-grade PDF/HTML reports with executive summaries

### 7. Cost Tracking & ROI Analysis Module (Tier 2+)
* **API Usage Logging:** Track API calls, tokens, costs per model
* **Cost Aggregation:** Calculate $/query, $/successful_output, cost per quality point
* **TCO Calculator:** Include infrastructure, developer overhead, API costs
* **ROI Dashboard:** Visualize cost-effectiveness and quality/cost tradeoffs

### 8. Historical Trend Database
* **Schema:** Time-indexed metrics storing daily/weekly aggregates for each AI model
* **Metrics:** Average compilation success rate, security issue counts, performance benchmarks, code quality scores
* **Retention:** Indefinite with optional archival to cold storage
* **Privacy Levels:** Private (organization only), Shared (with approved partners), Public (anonymized research)

## Data Flow Architecture

```
┌─────────────────────┐
│   User/API Input    │
│ (Code + Task + AI)  │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Orchestrator │◄──── Metadata enrichment
    │ (Pipeline)   │      (timestamps, versions)
    └──────┬───────┘
           │
    ┌──────┴──────────────────────┬─────────────────┐
    ▼                             ▼                 ▼
┌────────────┐         ┌──────────────────┐  ┌─────────────┐
│   Docker   │         │ Security Scanner │  │ Compliance  │
│  Sandbox   │         │  Suite (Parallel)│  │  Analyzer   │
│ (Execute)  │         └──────────────────┘  └─────────────┘
└──────┬─────┘                   │                   │
       │                         └────────┬──────────┘
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
            ┌─────────────────────┐
            │  Result Aggregator  │
            │   (JSON Builder)    │
            └──────┬──────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌─────────┐        ┌──────────────┐
   │ SQLite  │        │ InfluxDB/    │
   │ (Meta)  │        │ Prometheus   │
   └─────────┘        │ (Time-series)│
        │             └──────┬───────┘
        │                    │
        └────────┬───────────┘
                 ▼
     ┌─────────────────────────┐
     │  WebSocket Stream to    │
     │  Real-Time Dashboard    │
     └─────────────────────────┘
```

## Flow of Data (Detailed Example)

1. **Input:** User selects "Task B (JSON Threads)", "Model: GPT-4", "Language: Python"
2. **Orchestrator:**
   - Stores in temporary file: `temp_task_b_gpt4_20260216_143022.py`
   - Records metadata: timestamp, model version (GPT-4 Turbo 2024-11), language, task_id
3. **Parallel Processing:**
   - *Compiler:* Docker Python container runs file; captures stdout, stderr, exit code
   - *Tester:* Injects sample JSON data, verifies output matches expected format, measures execution time
   - *Security:* Runs Bandit on code, parses results (vulnerability count, severity levels)
   - *Compliance:* Checks for hardcoded secrets, unsafe patterns, OWASP violations
4. **Aggregation:**
   - Builds result JSON: `{compile_status: "success", functional_correctness: 0.95, security_issues: 2, exec_time_ms: 145, vulnerabilities: [{type: "hardcoded_secret", severity: "high", line: 23}]}`
5. **Storage:**
   - SQLite: Stores full record for historical reference
   - InfluxDB: Stores aggregated metrics for trend analysis
   - WebSocket: Streams result to dashboard in real-time
6. **Output:** Dashboard updates with new data point; historical trend chart reflects new benchmark

## Scalability Considerations

**Current (MVP):** Single-machine execution, SQLite local storage, WebSocket to local dashboard

**Phase 2 (Distributed):** 
- Kubernetes orchestration for Docker sandboxes
- InfluxDB cloud cluster for time-series data
- Elasticsearch for searchable code/findings
- API gateway for distributed client connections

**Phase 3+ (Enterprise SaaS):**
- Multi-tenant isolation
- Database replication across regions
- CDN for dashboard delivery
- Advanced RBAC for compliance auditing
