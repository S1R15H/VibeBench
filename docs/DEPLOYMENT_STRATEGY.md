# Deployment Strategy & Scaling

## Overview
This document outlines VibeBench deployment strategies across development, staging, production, and enterprise environments. It covers containerization, cloud infrastructure, high availability, disaster recovery, and operational best practices.

## Development Environment

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
