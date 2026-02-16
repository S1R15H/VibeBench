# Project Roadmap (Research Version)

## Executive Summary

VibeBench is a student research project (not a startup) targeting publication at academic venues. The timeline is 12 weeks (one semester) with realistic scope for a team of students with limited budget.

**Goal:** Produce a published research paper on "Comparative Evaluation of AI Code Generation Systems" with open-source framework and public dataset.

**Timeline:** 12 weeks → Conference submission → Publication

---

## Phase 1: MVP Implementation (Weeks 1-6)

**Goal:** Working benchmarking framework with all 8 tasks functional

### Week 1-2: Core Setup
* [ ] GitHub repository setup and contribution guidelines
* [ ] Python environment (venv/poetry) and dependencies
* [ ] Build **GUI Shell** (PyQt6, simple layout):
    * Task selection dropdown (A-H)
    * AI model selection (Copilot, GPT-4, Claude, Gemini)
    * "Run Benchmark" button
    * Progress text display
    * Results summary panel
* [ ] Create simple Docker image with Python + Node.js + PHP

### Week 2-3: Task Implementations
* [ ] **Task A:** Text file reading
* [ ] **Task B:** Multi-threaded JSON reading
* [ ] **Task C:** Text file writing
* [ ] **Task D:** Multi-threaded JSON writing
* [ ] **Task E:** ZIP archive creation
* [ ] **Task F:** MySQL database query
* [ ] **Task G:** MongoDB database query
* [ ] **Task H:** Password hashing (JavaScript/PHP)

**For each task:**
- [ ] Create test data file
- [ ] Write verification script
- [ ] Document expected output

### Week 3-4: Code Execution & Verification
* [ ] Implement simple orchestrator (single-threaded Python):
    - For each AI model:
      - Fetch code (API or manual)
      - Save to temp file
      - Run in Docker container
      - Verify output
      - Store result
      
* [ ] Implement task verifiers (unit tests):
    - Check compilation success
    - Check functional correctness
    - Measure execution time
    - Check memory usage

### Week 4-5: Security Analysis
* [ ] Integrate Bandit (Python security scanner)
* [ ] Integrate npm audit (JavaScript)
* [ ] Parse output → Extract vulnerability count + types
* [ ] Store security findings in database
* [ ] Create simple OWASP category mapping (manual)

### Week 5-6: Database & Reporting
* [ ] SQLite schema with Experiments table
* [ ] Store results: model, task, language, code, metrics
* [ ] CSV export functionality
* [ ] Simple text report (markdown)
* [ ] Manual testing of all 8 tasks with 1-2 AI models

**Deliverable at Week 6:**
- ✅ Working GUI
- ✅ All 8 tasks execute and verify
- ✅ Results stored in SQLite
- ✅ CSV export works
- ✅ Zero critical bugs

---

## Phase 2: API Integration & Data Collection (Weeks 7-9)

**Goal:** Collect benchmark data from 4 AI models

### Week 7: API Integration Setup
* [ ] **OpenAI (GPT-4 Turbo)**
  - [ ] API key from student accounts / free tier
  - [ ] Simple wrapper: `openai.ChatCompletion.create(...)`
  - [ ] Cost tracking per call
  
* [ ] **Anthropic (Claude 3 Opus/Sonnet)**
  - [ ] API setup
  - [ ] Basic integration
  
* [ ] **Google Gemini**
  - [ ] API setup (free tier available)
  - [ ] Basic integration
  
* [ ] **GitHub Copilot** (Manual)
  - [ ] Document prompts
  - [ ] Manual copy-paste workflow

### Week 7-8: Cost Management
* [ ] Set API budgets (e.g., $50 total for semester)
* [ ] Log costs per model per task
* [ ] Create cost summary report
* [ ] Use free/cheap models for testing (Gemini, Claude Sonnet)

### Week 8-9: Data Collection
* [ ] Run 10 iterations per model per task (40 benchmark runs)
* [ ] Store all results in SQLite
* [ ] Export as CSV for analysis
* [ ] Document any issues/edge cases

**Deliverable at Week 9:**
- ✅ ~320 benchmark records (4 models × 8 tasks × 10 runs)
- ✅ Cost tracking data
- ✅ Security vulnerability analysis
- ✅ Execution time metrics

---

## Phase 3: Analysis & Research Paper (Weeks 10-12)

**Goal:** Analyze results and write publishable research paper

### Week 10: Data Analysis
* [ ] Load CSV into pandas
* [ ] Compute summary statistics:
  - Compilation success rates (per model, per task)
  - Average execution time
  - Security issue counts by model
  - Cost per successful run
  
* [ ] Create simple visualizations:
  - Bar chart: Compilation success % (models vs tasks)
  - Bar chart: Security issues (models vs tasks)
  - Scatter plot: Quality vs Cost
  
* [ ] Statistical analysis:
  - Which model is most reliable?
  - Which tasks are hardest?
  - Security: Which types of issues are most common?

### Week 11: Paper Writing
* [ ] **Paper Structure:**
  1. Abstract (1/4 page): "We evaluated 4 AI coding assistants..."
  2. Introduction (1 page): Motivation, research questions
  3. Methodology (1 page): The 8 tasks, metrics, evaluation setup
  4. Results (2 pages): Graphs, tables, findings
  5. Discussion (1 page): What we learned, limitations
  6. Related Work (1/2 page): Other benchmarks
  7. Conclusion (1/4 page): Future work

* [ ] Create publication-ready figures (matplotlib)
* [ ] Tables of results (pandas → LaTeX)
* [ ] Write prose explaining findings

### Week 12: Cleanup & Submission
* [ ] Code cleanup (add comments, README)
* [ ] Push to GitHub (public repo)
* [ ] Create dataset (anonymized if needed)
* [ ] Write arXiv paper
* [ ] Submit to conference (FSE, ICSE, MSR, or EMSE)

**Deliverable at Week 12:**
- ✅ Research paper (4-6 pages)
- ✅ Open-source code on GitHub
- ✅ Public dataset (CSV files)
- ✅ Reproducibility notes

---

## Research Contributions (What We're Publishing)

### Finding 1: Model Capability Ranking
```
Task B (Multi-threaded JSON):
1. GPT-4 Turbo: 92% success, 2.3 security issues avg
2. Claude 3 Opus: 88% success, 1.8 security issues avg
3. Claude 3 Sonnet: 85% success, 2.1 security issues avg
4. Gemini Pro: 72% success, 4.2 security issues avg

→ Finding: GPT-4 is most reliable for concurrency
```

### Finding 2: Security Patterns
```
Most Common Security Issues:
- Hardcoded paths/passwords: 45% of all issues
- Missing input validation: 30%
- Race conditions: 15%
- SQL injection risk: 10%

→ Finding: Prompt engineering needed for security
```

### Finding 3: Cost vs Quality
```
Cost-Effectiveness:
- Gemini Pro: $0.0009 per task, 78% avg quality
- Claude Sonnet: $0.0045 per task, 85% avg quality
- GPT-4: $0.015 per task, 90% avg quality

→ Finding: Claude Sonnet best value for research
```

### Finding 4: Task Difficulty
```
Hardest Tasks (compilation success rate):
1. Task H (Password hashing): 68% (security matters)
2. Task B (Multi-threading): 75% (race conditions)
3. Task G (MongoDB): 82% (connection handling)

Easiest Tasks:
1. Task A (File reading): 95%
2. Task C (File writing): 93%

→ Finding: LLMs struggle with concurrency, security
```

---

## Timeline Overview

```
Week 1-2:    Core setup, GUI shell
Week 2-3:    Implement all 8 tasks
Week 3-4:    Code execution & verification
Week 4-5:    Security scanning integration
Week 5-6:    Database & reporting (DEMO READY)
─────────────────────────────────────────────
Week 7:      API integration for 4 models
Week 7-8:    Cost tracking setup
Week 8-9:    Data collection (320 runs)
─────────────────────────────────────────────
Week 10:     Analysis & visualizations
Week 11:     Paper writing
Week 12:     Code cleanup, submission
```

---

## Resource Requirements (Budget-Friendly)

### People
- 4-6 students (mix of junior/senior)
- 1 faculty advisor (guidance, not coding)
- Commitment: ~10 hours/week per student

### Hardware
- Existing laptops (no new purchases)
- Optional: Lab server for final runs (if available)
- Use existing university resources

### Software (FREE)
- Python (open-source)
- PyQt6 (open-source)
- Docker (free tier)
- GitHub (free public repo)
- SQLite (included in Python)

### APIs (CHEAP)
- **OpenAI:** ~$20-30 (use free trial credits first)
- **Anthropic:** Free beta access
- **Google Gemini:** Free tier available
- **GitHub Copilot:** Use free GitHub student account

**Total budget: $0-50** (optional, for better API access)

---

## Team Roles

| Role | Responsibility | Weeks |
|------|---|---|
| **Lead Backend Dev** | Orchestrator, task verifiers | 1-9 |
| **GUI Developer** | PyQt6 interface | 1-6 |
| **DevOps** | Docker setup, database | 2-6 |
| **Data Scientist** | Analysis, visualizations, paper | 8-12 |
| **Quality Assurance** | Testing, reproducibility | 3-9 |
| **Advisor** | Guidance, paper review | Throughout |

---

## Success Criteria (Research)

### Week 6 Demo
- ✅ GUI working
- ✅ All 8 tasks execute
- ✅ Results stored in database
- ✅ No critical bugs

### Week 9 Data Ready
- ✅ 320+ benchmark records
- ✅ Results CSV exportable
- ✅ Reproducible (same inputs = same outputs)
- ✅ Cost within budget

### Week 12 Paper Ready
- ✅ 4-6 page research paper
- ✅ Clear findings/contributions
- ✅ Publication-quality figures
- ✅ Code open-sourced on GitHub
- ✅ Dataset publicly available

---

## Publication Strategy

### Target Conferences (Listed by Tier)
1. **Tier 1 (Prestigious):**
   - ICSE (International Conference on Software Engineering)
   - ESEC/FSE (Foundations of Software Engineering)
   - MSR (Mining Software Repositories)

2. **Tier 2 (Solid):**
   - EMSE (Empirical Software Engineering)
   - ASE (Automated Software Engineering)

3. **Fallback:**
   - arXiv preprint (instant, free, citable)
   - Workshop papers
   - Student research track

### Timeline
- **Week 12:** Submit to arXiv
- **Week 12-13:** Polish and submit to conference
- **3-6 months:** Review process
- **6-9 months:** Presentation at conference (if accepted)

---

## Post-Publication (Optional Extensions)

If research goes well, students can extend for future semesters:

1. **Add new languages:** Rust, Go, TypeScript
2. **More AI models:** Once new APIs available
3. **Longer-term study:** Monthly updates over 1 year
4. **Prompt optimization:** Try improving prompts based on findings
5. **Fine-tuning study:** Does custom training help?

But **primary goal is publication within 12 weeks.**

---

## Known Limitations (Be Transparent)

Document in paper:
- Small dataset (40 runs per model - for reproducibility with budget constraints)
- 8 specific tasks (not comprehensive, but standardized)
- Older AI model versions (use free/cheap APIs)
- Single lab environment (not cloud deployment)
- Manual processes (not fully automated)

**These are OK for research.** Journals appreciate honesty about limitations.

---

## What We're NOT Doing

- ❌ Building production system (it's research framework)
- ❌ 100+ task benchmarks (8 is sufficient for publication)
- ❌ Real-time dashboards (static reports work)
- ❌ Multi-region cloud (overkill for research)
- ❌ 100,000 benchmark runs (too expensive, 320 sufficient for paper)
- ❌ Advanced ML predictions (descriptive analysis is better for research)
- ❌ White-label SaaS (publish findings, not product)