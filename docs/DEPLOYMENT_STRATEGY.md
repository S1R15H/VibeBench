# Deployment Strategy (Research Lab Version)

## Overview

VibeBench is designed to run on a single machine: laptop, lab server, or university workstation. No complex infrastructure, cloud accounts, or DevOps needed.

**Supported Environments:**
- 💻 Personal laptop (Windows, Mac, Linux)
- 🖥️ Lab server (Linux, shared by team)
- 📚 University computing cluster (if available)

---

## Development Environment (Local Machine)

### Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/S1R15H/VibeBench.git
cd VibeBench

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install backend dependencies and start API
cd backend
pip install -r requirements.txt
uvicorn api:app --reload &

# 4. Install frontend dependencies and start UI
cd ../frontend
npm install
npm run dev
```

### Backend Requirements.txt (Minimal)
```
fastapi
uvicorn
bandit==1.7.5
pymongo==4.6.1
mysql-connector-python==8.2.0
pandas==2.1.3
matplotlib==3.8.2
requests==2.31.0  # For API calls
```

### Optional: Docker (Safer Code Execution)

If you want code execution in Docker (recommended for safety):

```bash
# Build Docker image (one-time)
docker build -t vibebench .

# Now code will run in containers
```

**Simple Dockerfile:**
```dockerfile
FROM ubuntu:22.04

# Install languages
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    nodejs npm \
    php \
    mysql-client \
    default-jre \
    git

# Install security tools
RUN pip3 install bandit
RUN npm install -g eslint

# Copy test files
COPY test_data/ /app/test_data/

WORKDIR /app
CMD ["/bin/bash"]
```

---

## Lab Server Setup

### For Shared Lab Server

If your university provides a shared server, setup is even simpler:

```bash
# SSH into lab server
ssh username@lab-server.university.edu

# Create project directory
mkdir -p ~/projects/vibebench
cd ~/projects/vibebench

# Clone and setup (same as local)
git clone https://github.com/S1R15H/VibeBench.git
cd VibeBench/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backend API
nohup uvicorn api:app --host 0.0.0.0 --port 8000 &> api.log &

# Run frontend Next.js App
cd ../frontend
npm install
nohup npm run dev &> frontend.log &
```

### Access from Other Machines

Once running on lab server:

```bash
# From your laptop, SSH tunnel to access Next.js GUI
ssh -L 3000:127.0.0.1:3000 username@lab-server.university.edu

# Then open browser:
# http://localhost:3000
```

---

## Database Setup (No Admin Rights Needed)

### SQLite (Recommended - No Setup)

```bash
# SQLite is included with Python
# Just start the FastAPI backend - it creates experiments.db automatically
uvicorn api:app --reload

# Database file appears in project directory:
# ./experiments.db  (single file, ~1MB after 100 runs)
```

### MySQL (If Lab Provides It)

```bash
# Create database
mysql -h localhost -u your_user -p
> CREATE DATABASE vibebench_test;
> USE vibebench_test;
> source test_data/task_f/schema.sql
```

### MongoDB (If Lab Provides It)

```bash
# Connect to existing MongoDB
mongo mongodb://localhost:27017

# Database and collections auto-created on first write
```

---

## API Setup (API Keys)

### Step 1: Get API Keys (Most Free!)

```bash
# OpenAI (use free trial credits first)
# https://platform.openai.com/account/api-keys

# Anthropic (free beta)
# https://console.anthropic.com/

# Google Gemini (free tier available)
# https://ai.google.dev/

# GitHub Copilot (free for students)
# Use github.com/student free account
```

### Step 2: Configure API Keys (Secure)

Create `.env` file (NEVER commit to git):
```bash
# .env (git ignored)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

In Python code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY')
```

### Step 3: Budget Management

```python
# Simple cost tracking in code
COSTS = {
    'gpt-4': 0.015 / 1000,  # $ per token
    'claude-opus': 0.015 / 1000,
    'gemini-pro': 0.0009 / 1000,
}

def track_cost(model, tokens_used):
    cost = tokens_used * COSTS[model]
    print(f"Cost for this run: ${cost:.4f}")
```

**Budget:** Set alerts if spending > $50/semester

---

## Data Backup (Important!)

### Backup Strategy (Simple)

```bash
# Backup SQLite database weekly
cp experiments.db experiments.db.backup-$(date +%Y-%m-%d)

# Upload to GitHub (private repo)
git add experiments.db.backup-*
git commit -m "backup: $(date)"
git push

# Or use cloud storage (Google Drive, Dropbox, OneDrive)
cp experiments.db ~/Dropbox/vibebench/experiments.db
```

### Restore from Backup

```bash
# If database corrupted:
rm experiments.db
cp experiments.db.backup-2024-02-15 experiments.db
```

---

## Performance Considerations

### Laptop Specs (Minimum)

| Spec | Requirement |
|------|---|
| RAM | 8GB (16GB comfortable) |
| Storage | 20GB free (for benchmarks + results) |
| CPU | Dual-core (any modern processor) |
| Network | Stable internet (for API calls) |

### Typical Benchmark Runtime

```
Single benchmark (1 task, 1 AI model):
- API call: 5-10 seconds
- Code execution: 1-5 seconds
- Analysis: 2-3 seconds
- Total: 10-20 seconds

Full suite (8 tasks × 4 models):
- Time: ~10-15 minutes
- Data size: ~500KB per run
```

### Optimization Tips

If running slow:

```python
# Parallel execution (optional)
from concurrent.futures import ThreadPoolExecutor

# Run multiple tasks concurrently
with ThreadPoolExecutor(max_workers=2) as executor:
    results = executor.map(run_benchmark, tasks)

# But: Simpler (sequential) is better for research reproducibility
```

---

## Monitoring & Logging

### Simple Logging

```python
import logging

logging.basicConfig(
    filename='vibebench.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Started benchmark for {model}")
```

### Check Logs

```bash
# View recent logs
tail -f vibebench.log

# Search for errors
grep ERROR vibebench.log

# Check API costs
grep "cost:" vibebench.log | awk '{sum+=$NF} END {print sum}'
```

---

## Reproducibility

### For Running Same Benchmarks Again

```bash
# Note timestamps and conditions
# Example: "Ran on 2024-02-16 with GPT-4 turbo, Gemini, Claude Opus"

# Re-run same tests:
python src/cli.py \
  --model gpt-4-turbo \
  --model gemini-pro \
  --model claude-opus \
  --tasks A,B,C,H \
  --seed 42

# Compare results
python src/analysis/compare_runs.py run_20240216.csv run_20240301.csv
```

### Version Control for Reproducibility

```bash
# Tag stable versions
git tag v1.0-research -m "Version for paper submission"
git push --tags

# Others can reproduce:
git checkout v1.0-research
npm run dev (frontend) && uvicorn api:app (backend)
```

---

## Troubleshooting

### "API Key Invalid"
```bash
# Check .env file exists
cat .env

# Check API quota at provider's website
# https://platform.openai.com/account/billing/overview
```

### "Docker not found"
```bash
# Install Docker
# https://docs.docker.com/engine/install/

# Or skip Docker - run code directly (less safe but works)
```

### "Out of Memory"
```bash
# Check if running too many tasks
# Reduce batch size: run 2 tasks at a time instead of 8

# Or upgrade laptop RAM (if running many models)
```

### "Database locked"
```bash
# If multiple processes access SQLite simultaneously
# Use file locking (built into SQLite)

# Or upgrade to PostgreSQL if needed
```

---

## Publishing Dataset & Code

### For Research Reproducibility

```bash
# 1. Anonymize sensitive data
python src/utils/anonymize.py experiments.db

# 2. Export results
python src/export.py --format csv --output results.csv

# 3. Push to GitHub (public)
git add results.csv
git commit -m "feat: add benchmark results for paper"
git push

# 4. Archive on Zenodo (optional)
# https://zenodo.org/ - creates DOI for citations
```

### GitHub Public Repo

```
vibebench/
├── README.md              # How to use
├── src/                   # Code
├── test_data/             # Test cases
├── results.csv            # Benchmark data
├── analysis/              # Jupyter notebooks
├── paper.pdf              # Submitted/published paper
└── requirements.txt
```

---

## Optional: University Computing Cluster

If your university has HPC (High-Performance Computing):

```bash
# Example: SLURM job scheduler
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --mem=16GB

source ~/projects/vibebench/venv/bin/activate
python ~/projects/vibebench/src/benchmark.py --all-models
```

---

## Cost Summary

| Resource | Cost |
|----------|------|
| Development | Free (own laptop) |
| Git hosting | Free (GitHub) |
| API calls | $20-50 (for whole project) |
| Storage | Free (Dropbox/Google Drive) |
| Backup | Free (GitHub) |
| **Total** | **$20-50 / semester** |

---

## What You DON'T Need

- ❌ AWS/Azure/GCP cloud account
- ❌ Kubernetes
- ❌ Docker Swarm
- ❌ Load balancers
- ❌ CDN
- ❌ Multi-region replication
- ❌ Dedicated DevOps engineer
- ❌ CI/CD pipelines (GitHub Actions optional)

---

## Summary: From Zero to Running

```
1. Clone repo (2 min)
2. Setup Python venv (2 min)
3. Install dependencies (3 min)
4. Get API keys (5 min)
5. Run GUI (1 min)
6. Run first benchmark (30 sec)

Total: ~13 minutes to first results ✓
```

That's it! Ready for research.
