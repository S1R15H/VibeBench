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

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run GUI
python src/gui.py
```

### Requirements.txt (Minimal)
```
PyQt6==6.6.1
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
cd VibeBench
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with nohup (keeps running if you disconnect)
nohup python src/gui.py &> vibebench.log &
```

### Access from Other Machines

Once running on lab server:

```bash
# From your laptop, SSH tunnel to access GUI
ssh -L 5000:127.0.0.1:5000 username@lab-server.university.edu

# Then open browser:
# http://localhost:5000
```

---

## Database Setup (No Admin Rights Needed)

### SQLite (Recommended - No Setup)

```bash
# SQLite is included with Python
# Just run VibeBench - it creates experiments.db automatically
python src/gui.py

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
python src/gui.py
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


### Local Machine Setup
```bash
# Prerequisites
- Docker & Docker Compose 1.29+
- Python 3.10+
- SQLite3
- Git

# Quick Start
git clone https://github.com/S1R15H/VibeBench.git
cd VibeBench
docker-compose -f docker-compose.dev.yml up -d
python src/setup_dev_environment.py
pytest tests/
```

### Docker Compose (Dev)
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  vibebench-core:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"  # Backend API
      - "3000:3000"  # Frontend dashboard
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      VIBEBENCH_ENV: development
      DEBUG: 'true'
    depends_on:
      - mysql
      - mongodb

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: dev_password
      MYSQL_DATABASE: vibebench_test
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./test_data/task_f/schema.sql:/docker-entrypoint-initdb.d/

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      INFLUXDB_ADMIN_USER: admin
      INFLUXDB_ADMIN_PASSWORD: dev_password
    volumes:
      - influxdb_data:/var/lib/influxdb2

volumes:
  mysql_data:
  mongo_data:
  influxdb_data:
```

---

## Staging Environment

### Purpose
- Pre-production testing
- Load testing
- Security scanning
- Integration testing with real APIs

### Infrastructure
```
┌─────────────────────────────────────────────────┐
│        Kubernetes Cluster (staging)              │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  VibeBench   │  │  VibeBench   │ (Replicas)│
│  │  Pod (main)  │  │  Pod (main)  │           │
│  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                    │
│  ┌──────┴─────────────────┴──────┐            │
│  │      Service (LoadBalancer)   │            │
│  └─────────────────────────────────┘           │
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   MySQL    │  │  MongoDB   │  │InfluxDB  │ │
│  │ (stateful) │  │ (stateful) │  │(stateful)│ │
│  └────────────┘  └────────────┘  └──────────┘ │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Kubernetes Deployment
```yaml
# k8s/staging/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vibebench-core-staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vibebench-core
      env: staging
  template:
    metadata:
      labels:
        app: vibebench-core
        env: staging
    spec:
      containers:
      - name: vibebench-core
        image: vibebench:latest-staging
        ports:
        - containerPort: 5000
        env:
        - name: VIBEBENCH_ENV
          value: staging
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### StatefulSets for Databases
```yaml
# k8s/staging/mysql-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-staging
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: root-password
  volumeClaimTemplates:
  - metadata:
      name: mysql-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

### Automated Testing in Staging
```yaml
# .github/workflows/staging-deploy.yml
name: Deploy to Staging
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        options: >-
          --health-cmd="mysqladmin ping" 
          --health-interval=10s 
          --health-timeout=5s 
          --health-retries=5
      mongodb:
        image: mongo:6.0
  
  deploy:
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t vibebench:latest-staging .
    - name: Push to registry
      run: docker push gcr.io/vibebench/core:latest-staging
    - name: Deploy to GKE
      run: kubectl set image deployment/vibebench-core-staging core=gcr.io/vibebench/core:latest-staging
    - name: Run smoke tests
      run: pytest tests/smoke_tests.py -v
```

---

## Production Environment

### High-Level Architecture
```
┌────────────────────────────────────────────────────────┐
│              Global Load Balancer (CloudFlare)          │
└──────────────┬─────────────────────────────┬───────────┘
               │ Primary Region              │ Secondary Region
        ┌──────▼────────────┐         ┌──────▼────────────┐
        │   GKE Cluster     │         │   GKE Cluster     │
        │   (us-central1)   │         │   (eu-west1)      │
        │                   │         │                   │
        │ ┌───────────────┐ │         │ ┌───────────────┐ │
        │ │ VibeBench Pod │ │         │ │ VibeBench Pod │ │
        │ │ (n1-std-4, x3)│ │         │ │ (n1-std-4, x2)│ │
        │ └───────────────┘ │         │ └───────────────┘ │
        │                   │         │                   │
        └──────┬────────────┘         └──────┬────────────┘
               │                             │
        ┌──────▼────────────────────────────▼──────┐
        │    Cloud SQL (HA MySQL - Multi-region)   │
        │    - Automatic failover (< 2 min)        │
        │    - Daily backups (30-day retention)    │
        │    - Read replicas for analytics         │
        └───────────────────────────────────────────┘
               │
        ┌──────▼────────────────────────┐
        │  CloudSQL for MongoDB (Atlas) │
        │  - Replica Set (3 nodes)      │
        │  - Automatic sharding         │
        │  - Continuous backup          │
        └───────────────────────────────┘
               │
        ┌──────▼────────────────────────┐
        │    InfluxDB Cloud (Time-series)
        │    - 30-day retention (main)   │
        │    - Unlimited retention (cold)│
        │    - Geo-replicated backup     │
        └───────────────────────────────┘
```

### GKE Cluster Configuration (Production)
```yaml
# gke-cluster.yaml (Terraform)
resource "google_container_cluster" "primary" {
  name     = "vibebench-prod"
  location = "us-central1"

  # Cluster configuration
  initial_node_count       = 3
  remove_default_node_pool = true
  logging_service          = "logging.googleapis.com/kubernetes"
  monitoring_service       = "monitoring.googleapis.com/kubernetes"

  # Network
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # Security
  network_policy {
    enabled = true
  }

  # IP address management
  cluster_secondary_range_name = "pods"
  services_secondary_range_name = "services"
}

# Node Pool for VibeBench
resource "google_container_node_pool" "primary_nodes" {
  name           = "vibebench-pool"
  cluster        = google_container_cluster.primary.name
  node_count     = 3

  node_config {
    preemptible  = false
    machine_type = "n1-standard-4"
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    disk_size_gb = 100
    disk_type    = "pd-ssd"
  }

  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }
}
```

### Production Helm Chart
```yaml
# helm/vibebench/values.yaml
replicaCount: 3

image:
  repository: gcr.io/vibebench/core
  tag: "1.0.0"
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

persistence:
  enabled: true
  storageClass: "fast-ssd"
  size: 100Gi

ingress:
  enabled: true
  className: "gce"
  annotations:
    cert.gardener.cloud/issuer-name: letsencrypt-prod
  hosts:
    - host: vibebench.io
      paths:
        - path: /
          pathType: Prefix
        - path: /api
          pathType: Prefix
```

### Database Disaster Recovery

**MySQL Backup Strategy:**
```bash
#!/bin/bash
# backup-mysql-prod.sh
# Runs daily at 02:00 UTC

BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/vibebench_${BACKUP_TIME}.sql.gz"

# Local backup
mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD \
  --all-databases --quick --lock-tables=false | gzip > $BACKUP_FILE

# Upload to GCS (multi-region)
gsutil -m cp $BACKUP_FILE gs://vibebench-backups-us/
gsutil -m cp $BACKUP_FILE gs://vibebench-backups-eu/

# Verify backup
gzip -t $BACKUP_FILE && echo "✓ Backup valid" || echo "✗ Backup corrupted"

# Clean old backups (keep 30 days)
find /backups -name "vibebench_*.sql.gz" -mtime +30 -delete
```

**Recovery Procedure:**
```bash
# Restore from backup (estimated time: 15 minutes)
gsutil cp gs://vibebench-backups-us/vibebench_${RESTORE_DATE}.sql.gz - | \
  gzip -d | mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD

# Verify data integrity
mysql -e "SELECT COUNT(*) FROM vibebench.experiments;" > /tmp/count.txt
```

**RTO/RPO Targets:**
- Recovery Time Objective (RTO): < 30 minutes
- Recovery Point Objective (RPO): < 1 hour
- Backup retention: 30 days local, 90 days archived

---

## Monitoring & Observability

### Logging Stack (ELK)
```yaml
# Elasticsearch for centralized logging
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - '/var/log/containers/*${NAMESPACE}*/*.log'
    
    processors:
      - add_kubernetes_metadata:
          in_cluster: true
    
    output.elasticsearch:
      hosts: ["${ELASTICSEARCH_HOST}:9200"]
      username: "${ELASTICSEARCH_USER}"
      password: "${ELASTICSEARCH_PASSWORD}"
```

### Metrics (Prometheus)
```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'vibebench-core'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: vibebench-core
      - source_labels: [__meta_kubernetes_pod_port_name]
        action: keep
        regex: metrics

  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:3306']

  - job_name: 'mongodb'
    static_configs:
      - targets: ['localhost:27017']
```

### Alerts (AlertManager)
```yaml
# alert-rules.yaml
groups:
  - name: vibebench
    rules:
    - alert: HighErrorRate
      expr: rate(vibebench_errors_total[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"

    - alert: SlowBenchmarkRun
      expr: vibebench_benchmark_duration_seconds > 300
      for: 10m
      annotations:
        summary: "Benchmark run exceeding 5 minutes"

    - alert: DatabaseConnectionPoolExhausted
      expr: vibebench_db_pool_exhausted == 1
      for: 1m
      annotations:
        summary: "Database connection pool at max"
```

### Dashboard (Grafana)
- Real-time benchmark progress
- API latency percentiles (p50, p95, p99)
- Error rates and types
- Database query performance
- Cost tracking per AI model
- Pod resource utilization

---

## Scaling Strategy

### Horizontal Scaling
- Auto-scale based on CPU utilization (70%) or request rate
- Min 3 replicas (HA), Max 10 replicas
- Pod disruption budgets maintain availability during updates
- Circuit breaker pattern for downstream API calls

### Vertical Scaling
- Start: n1-standard-4 (4 vCPU, 15GB RAM)
- Under load: n1-standard-8 (8 vCPU, 30GB RAM)
- Evaluation: Memory usage patterns, CPU throttling

### Database Scaling
- MySQL: Read replicas for analytics queries
- MongoDB: Sharding by task_id/ai_model
- InfluxDB: Distributed cluster with 3+ nodes

---

## Cost Optimization

### Instance Sizing
```
Development: nano instance (0.5 vCPU, 1GB RAM) - $10/month
Staging:     small instance (2 vCPU, 4GB RAM) - $50/month
Production:  medium instances x3 (4 vCPU, 15GB RAM) - $600/month
```

### Reserved Instances (RI)
- 1-year RI: 30% discount vs. on-demand
- Savings plans for sustained workloads
- Spot instances for non-critical jobs (batch processing)

### Storage Optimization
- InfluxDB retention: 30 days hot, 90 days warm, 1 year cold (archive)
- Compress logs after 7 days
- Delete benchmark artifacts after 60 days

---

## Security Best Practices

### Network Security
```yaml
# Network Policy: Restrict traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vibebench-netpol
spec:
  podSelector:
    matchLabels:
      app: vibebench-core
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 3306  # MySQL
    - protocol: TCP
      port: 27017  # MongoDB
    - protocol: TCP
      port: 443  # HTTPS for APIs
```

### Secrets Management
```bash
# Use GCP Secret Manager (not hardcoded or ConfigMaps)
gcloud secrets create vibebench-db-password --replication-policy="automatic"
gcloud secrets create vibebench-api-keys --replication-policy="automatic"

# Access in Kubernetes
kubectl create secret generic db-secrets \
  --from-literal=password=$(gcloud secrets versions access latest --secret=vibebench-db-password)
```

### TLS/SSL Certificates
- Let's Encrypt (automated renewal)
- Minimum TLS 1.2
- Certificate pinning for API endpoints
- HSTS headers enabled

### Access Control (RBAC)
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: vibebench-deployer
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "update"]
- apiGroups: [""]
  resources: ["pods", "pods/logs"]
  verbs: ["get", "list"]
```

---

## Enterprise Deployment (White-Label SaaS)

### Multi-Tenant Architecture
```
┌─────────────────────────────────────────┐
│     Shared Infrastructure Layer          │
│  (Kubernetes, Networking, Monitoring)   │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
┌───▼──┐      ┌───▼──┐      ┌──▼───┐      ┌──▼───┐
│Tenant│      │Tenant│      │Tenant│      │Tenant│
│  A   │      │  B   │      │  C   │      │  D   │
│(DB)  │      │(DB)  │      │(DB)  │      │(DB)  │
└──────┘      └──────┘      └──────┘      └──────┘
```

### Tenant Isolation
- Database isolation: Separate schema or database per tenant
- Namespace isolation: Kubernetes namespace per tenant
- Network isolation: Egress rules prevent cross-tenant traffic
- Resource quotas: Prevent one tenant exhausting resources

### Deployment Process
```bash
# Provision new tenant
terraform apply -var="tenant_name=acme-corp" -var="tier=enterprise"

# Creates:
# - Kubernetes namespace: acme-corp-vibebench
# - Database schema: acme_corp_vibebench
# - Secrets and RBAC
# - Custom DNS: acme-corp.vibebench.io
```

---

## Operational Runbooks

### Common Issues & Resolution

**Issue: Benchmark Hangs (Process Timeout)**
```bash
# Identify hanging pod
kubectl get pods | grep vibebench-core | grep Running

# Check container logs
kubectl logs <pod-name> -f

# Kill hanging container (graceful)
kubectl delete pod <pod-name>

# Pod automatically respawned by ReplicaSet
# Max 5 retries before marking as failed
```

**Issue: Database Connection Pool Exhaustion**
```bash
# Check active connections
SELECT COUNT(*) FROM information_schema.processlist;

# Identify slow queries
SELECT * FROM mysql.slow_log ORDER BY start_time DESC;

# Restart connection pool
# (triggers rolling restart of all pods)
kubectl rollout restart deployment/vibebench-core-prod
```

**Issue: High Latency**
```bash
# Check P99 latency distribution
curl https://monitoring.vibebench.io/api/metrics/latency | jq '.p99'

# Scale up if >1 second
kubectl scale deployment vibebench-core-prod --replicas=5

# Or check for resource contention
kubectl top nodes
kubectl top pods -n vibebench
```

---

## Change Management

### Blue-Green Deployment
```bash
# Deploy new version to "green" environment
kubectl set image deployment/vibebench-core-green \
  core=gcr.io/vibebench/core:1.1.0

# Wait for green to be healthy
kubectl rollout status deployment/vibebench-core-green

# Switch traffic from blue to green (switch service selector)
kubectl patch service vibebench-core -p \
  '{"spec":{"selector":{"version":"green"}}}'

# Keep blue running for 24 hours for quick rollback
```

### Rollback Procedure
```bash
# If issues detected:
kubectl patch service vibebench-core -p \
  '{"spec":{"selector":{"version":"blue"}}}'

# Rollback takes < 10 seconds
```

---

## Compliance & Audit

### Audit Logging
- All API calls logged (request, response, user, timestamp)
- Immutable audit logs (Cloud Audit Logs with indefinite retention)
- Compliance reports exportable for SOC2/HIPAA/PCI-DSS

### Data Retention Policy
- Raw benchmark data: 30 days
- Aggregated metrics: Indefinite
- Audit logs: 7 years (compliance requirement)
- Automated purging of PII (if applicable)
