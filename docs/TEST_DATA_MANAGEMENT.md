# Test Data Management & Reproducibility Strategy

## Overview
VibeBench requires standardized, versioned test data across all benchmark runs to ensure reproducibility and valid comparisons across AI models. This document specifies the test case structure, sample data management, database seeding procedures, and reproducibility guardrails.

## Test Case Structure

### Task A: Text File Reading
**Objective:** Read structured text data and parse it correctly

**Test Data File:** `test_data/task_a/input.txt`
```
Customer,Order ID,Amount,Date
Alice,ORD001,150.50,2024-01-15
Bob,ORD002,200.00,2024-01-16
Charlie,ORD003,75.25,2024-01-17
```

**Expected Output:**
```json
{
  "total_records": 3,
  "total_amount": 425.75,
  "date_range": ["2024-01-15", "2024-01-17"],
  "valid": true
}
```

**Verification Criteria:**
- File parsed successfully (no exceptions)
- Correct number of records extracted (3)
- Numerical calculations accurate (sum = 425.75)
- Date parsing correct
- Output format matches JSON schema

---

### Task B: JSON File Reading with Multi-Threading
**Objective:** Read JSON file with multi-threaded access and aggregate results

**Test Data File:** `test_data/task_b/input.json`
```json
{
  "data_entries": [
    {"id": 1, "value": 100, "category": "A"},
    {"id": 2, "value": 200, "category": "B"},
    {"id": 3, "value": 150, "category": "A"},
    {"id": 4, "value": 300, "category": "C"},
    {"id": 5, "value": 250, "category": "B"}
  ]
}
```

**Thread Configuration:**
- Number of threads: 3
- Chunk size: 2 records per thread
- Timeout: 30 seconds

**Expected Output:**
```json
{
  "total_records_processed": 5,
  "total_value": 1000,
  "category_totals": {
    "A": 250,
    "B": 450,
    "C": 300
  },
  "threads_spawned": 3,
  "execution_time_ms": "<<varies>>",
  "thread_safety_verified": true
}
```

**Verification Criteria:**
- All records processed exactly once (no duplicates, no skipped)
- Correct aggregation across threads
- Actual thread count >= requested threads
- No race conditions detected (verify via inspection/profiling)
- Output matches expected schema

---

### Task C: Text File Writing
**Objective:** Write structured data to text file with correct formatting

**Input Data:**
```json
{
  "title": "Q4 Sales Report",
  "records": [
    {"region": "North", "sales": 50000},
    {"region": "South", "sales": 45000},
    {"region": "East", "sales": 55000}
  ]
}
```

**Expected Output File:** `test_data/task_c/output.txt`
```
Q4 Sales Report
===============
North: 50000
South: 45000
East: 55000
Total: 150000
```

**Verification Criteria:**
- File created successfully
- All data written correctly
- Formatting matches expected output exactly
- File is readable and valid UTF-8
- File permissions set correctly (readable by framework)

---

### Task D: JSON File Writing with Multi-Threading
**Objective:** Write aggregated data to JSON file using multiple threads

**Input Data:** Same as Task B (5 records, 3 categories)

**Expected Output File:** `test_data/task_d/output.json`
```json
{
  "generated_timestamp": "2024-02-16T14:30:22Z",
  "thread_count": 3,
  "records": [
    {"id": 1, "value": 100, "category": "A", "processed_by_thread": 0},
    {"id": 2, "value": 200, "category": "B", "processed_by_thread": 1},
    {"id": 3, "value": 150, "category": "A", "processed_by_thread": 2},
    {"id": 4, "value": 300, "category": "C", "processed_by_thread": 0},
    {"id": 5, "value": 250, "category": "B", "processed_by_thread": 1}
  ],
  "summary": {
    "total_records": 5,
    "total_value": 1000
  }
}
```

**Verification Criteria:**
- JSON file is valid and parseable
- All records written exactly once
- Correct data type for each field
- Thread IDs properly recorded (if applicable)
- File size > 0 and < 100KB (reasonable bounds)

---

### Task E: External Archive Creation
**Objective:** Create ZIP archive by calling external application

**Input File:** `test_data/task_e/sample.txt`
```
This is a sample file to be archived.
It contains multiple lines of text.
For testing purposes only.
```

**Expected Output:** `test_data/task_e/output.zip`

**Verification Criteria:**
- ZIP file created successfully
- ZIP file is valid (passes zip integrity check)
- Original file present inside archive
- Archive contains expected compression ratio (> 10% for text)
- Archive can be extracted without errors
- Extracted content matches original

**Edge Cases Tested:**
- Very small files (< 100 bytes)
- Unicode content
- Large files (> 10MB)

---

### Task F: MySQL Database Integration
**Objective:** Connect to MySQL and retrieve sample data

**Database Setup:**
```sql
CREATE DATABASE vibebench_test;
USE vibebench_test;

CREATE TABLE employees (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(50),
  salary INT,
  hire_date DATE
);

INSERT INTO employees VALUES
(1, 'Alice Johnson', 'Engineering', 95000, '2022-03-15'),
(2, 'Bob Smith', 'Sales', 75000, '2021-08-20'),
(3, 'Charlie Brown', 'Engineering', 90000, '2023-01-10'),
(4, 'Diana Prince', 'HR', 80000, '2022-11-05'),
(5, 'Eve Wilson', 'Finance', 85000, '2023-05-12');
```

**Database Connection:** 
- Host: `localhost` (or Docker bridge)
- Port: `3306`
- User: `vibebench_user`
- Password: `vibebench_test_pwd`
- Database: `vibebench_test`

**Expected Output:**
```json
{
  "connection_status": "success",
  "query_executed": "SELECT * FROM employees WHERE department='Engineering'",
  "records_returned": 2,
  "sample_record": {
    "id": 1,
    "name": "Alice Johnson",
    "department": "Engineering",
    "salary": 95000,
    "hire_date": "2022-03-15"
  },
  "execution_time_ms": "<<varies>>"
}
```

**Verification Criteria:**
- Connection established without errors
- SQL query executed successfully
- Correct number of records returned
- Data types correct (int, string, date)
- No sensitive data exposure
- Connection properly closed

---

### Task G: MongoDB Database Integration
**Objective:** Connect to MongoDB and retrieve sample data

**Database Setup:**
```javascript
db.createCollection("products");
db.products.insertMany([
  { _id: 1, name: "Laptop", category: "Electronics", price: 1200, stock: 15 },
  { _id: 2, name: "Mouse", category: "Accessories", price: 30, stock: 150 },
  { _id: 3, name: "Monitor", category: "Electronics", price: 400, stock: 45 },
  { _id: 4, name: "Keyboard", category: "Accessories", price: 120, stock: 80 },
  { _id: 5, name: "Headphones", category: "Accessories", price: 200, stock: 60 }
]);
```

**Database Connection:**
- Host: `localhost`
- Port: `27017`
- Database: `vibebench_test`
- Collection: `products`
- No authentication (test environment)

**Expected Output:**
```json
{
  "connection_status": "success",
  "collection": "products",
  "query": {"category": "Electronics"},
  "documents_found": 2,
  "sample_document": {
    "_id": 1,
    "name": "Laptop",
    "category": "Electronics",
    "price": 1200,
    "stock": 15
  },
  "execution_time_ms": "<<varies>>"
}
```

**Verification Criteria:**
- Connection established successfully
- Query executed correctly
- Correct number of documents returned
- Document structure matches schema
- Numeric values correct
- Connection properly closed

---

### Task H: Web Authentication (Password Hashing)
**Objective:** Implement secure password hashing and verification

**Test Input:**
```json
{
  "username": "testuser",
  "password": "SecureP@ssw0rd!",
  "action": "hash_and_verify"
}
```

**Expected Output:**
```json
{
  "username": "testuser",
  "hash_algorithm": "bcrypt",
  "hash_rounds": 12,
  "hashed_password": "$2b$12$...",
  "hash_length": 60,
  "verification_test": {
    "correct_password_verified": true,
    "wrong_password_rejected": true
  },
  "security_score": "A",
  "vulnerabilities": []
}
```

**Verification Criteria:**
- Password properly hashed (bcrypt, argon2, PBKDF2, or scrypt)
- Hash is not reversible
- Same password produces different hash (due to salt)
- Verification function works correctly
- No common vulnerabilities (plain text storage, weak algorithm, etc.)
- HTML sanitization applied if web-embeddable

---

## Test Data Versioning

### Version Control Strategy
```
test_data/
├── versions/
│   ├── v1.0/
│   │   ├── task_a/
│   │   ├── task_b/
│   │   └── ...
│   ├── v1.1/
│   │   └── ...
│   └── v2.0/
│       └── ...
├── current/ -> v2.0/  # Symlink to current version
└── manifest.json
```

**Manifest file** (`test_data/manifest.json`):
```json
{
  "version": "2.0",
  "created_date": "2024-02-16",
  "description": "Test data v2.0 with enhanced edge cases",
  "changes_from_v1": [
    "Task B: Added larger dataset (5 -> 10 records)",
    "Task H: Added HTML injection test case",
    "Task E: Added unicode filename test"
  ],
  "checksums": {
    "task_a": "sha256:abc123...",
    "task_b": "sha256:def456...",
    "task_c": "sha256:ghi789...",
    "task_d": "sha256:jkl012...",
    "task_e": "sha256:mno345...",
    "task_f": "sha256:pqr678...",
    "task_g": "sha256:stu901...",
    "task_h": "sha256:vwx234..."
  }
}
```

### Backward Compatibility
- Maintain at least 2 previous versions
- Document breaking changes
- Provide migration guide for old benchmarks

---

## Database Seeding Procedures

### Automated Setup Script
```python
# test_data/setup_databases.py
import subprocess
import json
import time

def setup_mysql():
    """Initialize MySQL test database"""
    sql_script = open('test_data/task_f/schema.sql').read()
    
    result = subprocess.run([
        'mysql', '-h', 'localhost', '-u', 'root', '-p${MYSQL_ROOT_PASSWORD}'
    ], input=sql_script, capture_output=True)
    
    assert result.returncode == 0, "MySQL setup failed"
    print("✓ MySQL database initialized")

def setup_mongodb():
    """Initialize MongoDB test database"""
    from pymongo import MongoClient
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['vibebench_test']
    
    # Drop existing collections
    db.products.drop()
    
    # Insert test data
    data = json.load(open('test_data/task_g/seed_data.json'))
    db.products.insert_many(data)
    
    print("✓ MongoDB database initialized")

def verify_setup():
    """Verify all databases are accessible"""
    # MySQL check
    result = subprocess.run(['mysql', '-u', 'vibebench_user', 
                            '-p${VIBEBENCH_DB_PASSWORD}', 
                            'vibebench_test', '-e', 'SELECT COUNT(*) FROM employees'],
                           capture_output=True)
    assert result.returncode == 0
    
    # MongoDB check
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    assert client['vibebench_test'].products.count_documents({}) == 5
    
    print("✓ All databases verified")

if __name__ == '__main__':
    setup_mysql()
    setup_mongodb()
    verify_setup()
```

### Docker Compose Setup
```yaml
# test_data/docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: vibebench_test
      MYSQL_USER: vibebench_user
      MYSQL_PASSWORD: vibebench_test_pwd
    ports:
      - "3306:3306"
    volumes:
      - ./test_data/task_f/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - ./test_data/task_g/seed_data.json:/seed/seed_data.json
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Reproducibility Guardrails

### Deterministic Execution
1. **Fixed Random Seeds:** If any task uses randomization, seed with constant
2. **Timezone Neutrality:** Use UTC for all timestamps, never local time
3. **Floating-Point Precision:** Round to 2 decimal places for monetary values
4. **File Permissions:** Ensure consistent umask (0o644 for files, 0o755 for dirs)

### Timing Considerations
- Task execution times vary by system load; store ranges not exact values
- Example: `execution_time_ms: {"min": 100, "max": 200, "expected": 150}`

### Environmental Variables
```bash
# These must be set identically across all benchmark runs
export VIBEBENCH_TEST_VERSION=2.0
export VIBEBENCH_SEED=42
export VIBEBENCH_TIMEZONE=UTC
export VIBEBENCH_FLOAT_PRECISION=2
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
```

### Pre-Run Validation Checklist
```python
def pre_run_validation():
    checks = [
        ("Test data version matches manifest", check_test_data_version),
        ("All databases are seeded", check_database_seeding),
        ("Required files exist", check_required_files),
        ("File checksums valid", check_file_integrity),
        ("Environment variables set", check_env_variables),
        ("Docker containers ready", check_docker_health),
        ("No stale processes", check_stale_processes),
    ]
    
    for check_name, check_fn in checks:
        try:
            check_fn()
            print(f"✓ {check_name}")
        except AssertionError as e:
            print(f"✗ {check_name}: {e}")
            raise
```

---

## Test Data Maintenance

### Updating Test Data (Versioning Process)
1. Create new version directory: `test_data/versions/v2.1/`
2. Update test data files with new/improved test cases
3. Update `manifest.json` with version and checksums
4. Update `current/` symlink
5. Commit with descriptive message: `chore: bump test data to v2.1 - add edge case for unicode filenames`
6. Announce deprecation of old version (60-day support window)

### Archival & Long-Term Storage
- Old test data versions archived to cold storage after 1 year
- Full dataset backups taken monthly
- S3/GCS bucket for offsite archival with versioning enabled

---

## Test Execution Validation

### Benchmark Run Report
```json
{
  "benchmark_id": "bench_20240216_143022",
  "test_data_version": "2.0",
  "timestamp": "2024-02-16T14:30:22Z",
  "environment": {
    "python_version": "3.11.8",
    "docker_version": "24.0.6",
    "os": "Ubuntu 22.04",
    "timezone": "UTC"
  },
  "results": [
    {
      "task_id": "A",
      "ai_model": "gpt-4-turbo",
      "status": "passed",
      "test_data_checksum": "abc123...",
      "output_matches_expected": true
    },
    ...
  ],
  "reproducibility_score": "99.5%"
}
```

This ensures every benchmark run is traceable and reproducible.
