# Test Data Management (Research Version)

## Overview
VibeBench uses simple, standardized test data for the 8 programming tasks. The focus is on reproducibility and clarity, not complex versioning systems.

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
- Language supported: AI produced a `.py` file for Python (Factor 1)
- File parsed successfully (no exceptions) — Req 2.1
- Compilation warnings captured from stderr — Req 2.3
- Correct number of records extracted (3)
- Numerical calculations accurate (sum = 425.75)
- Date parsing correct
- Output format matches JSON schema — Req 2.2
- Readability: cyclomatic complexity ≤ 5; comment density ≥ 0.10 — Factor 4

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
- Language supported: AI produced a valid file for the requested language (Factor 1)
- All records processed exactly once (no duplicates, no skipped) — Req 2.2
- Correct aggregation across threads
- Actual thread count >= requested threads
- No race conditions detected (verify via inspection/profiling) — Factor 2
- Compilation warnings captured from stderr — Req 2.3
- Output matches expected schema
- Readability: cyclomatic complexity checked; comment density logged — Factor 4

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
- Language supported: AI produced a valid text output file (Factor 1)
- File created successfully — Req 2.1
- Compilation warnings captured from stderr — Req 2.3
- All data written correctly — Req 2.2
- Formatting matches expected output exactly
- File is readable and valid UTF-8
- File permissions set correctly (readable by framework)
- Readability: comment density and cyclomatic complexity logged — Factor 4

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
- Language supported: AI produced a valid JSON-writing file (Factor 1)
- JSON file is valid and parseable — Req 2.1 / 2.2
- All records written exactly once
- Correct data type for each field
- Thread IDs properly recorded (if applicable)
- Compilation warnings captured from stderr — Req 2.3
- File size > 0 and < 100KB (reasonable bounds)
- Readability: cyclomatic complexity and comment density logged — Factor 4

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
- Language supported: AI produced a valid archiving script (Factor 1)
- ZIP file created successfully — Req 2.1 / 2.2
- ZIP file is valid (passes zip integrity check)
- Original file present inside archive
- Archive contains expected compression ratio (> 10% for text)
- Archive can be extracted without errors
- Extracted content matches original
- Compilation warnings captured from stderr — Req 2.3
- Readability: comment density logged — Factor 4

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
- Language supported: AI produced a valid DB connection script (Factor 1)
- Connection established without errors — Req 2.1
- Compilation warnings captured from stderr — Req 2.3
- SQL query executed successfully
- Correct number of records returned — Req 2.2
- Data types correct (int, string, date)
- No sensitive data exposure — Factor 3
- Connection properly closed
- Readability: cyclomatic complexity and comment density logged — Factor 4

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
- Language supported: AI produced a valid MongoDB script (Factor 1)
- Connection established successfully — Req 2.1
- Compilation warnings captured from stderr — Req 2.3
- Query executed correctly
- Correct number of documents returned — Req 2.2
- Document structure matches schema
- Numeric values correct
- Connection properly closed
- Readability: comment density and complexity logged — Factor 4

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
- Language supported: AI produced valid JS/PHP code embeddable in a web page (Factor 1)
- Password properly hashed (bcrypt, argon2, PBKDF2, or scrypt) — Req 2.1 / 2.2
- Hash is not reversible
- Same password produces different hash (due to salt)
- Verification function works correctly
- No common vulnerabilities (plain text storage, weak algorithm, etc.) — Req 2.4 / Factor 3
- Security mitigations generated for any findings (Factor 3)
- Compilation warnings captured from stderr — Req 2.3
- HTML sanitization applied if web-embeddable
- Readability: comment density and complexity logged — Factor 4

---

## Test Data Tracking

All test data is tracked in Git at `test_data/`. This ensures reproducibility—any benchmark run can be traced to exact test data via Git commit hash.

**No versioning system needed:** Since this is a student research project with a single 12-week timeline, all benchmark runs use the same test data version. If tasks change mid-project, simply commit the update and document when the change occurred in the research paper.

---

## Setting Up Databases (Optional)

For Tasks F and G, you need MySQL and MongoDB running locally. 

**Easiest approach:** Use Docker
```bash
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.0
docker run -d --name mongodb -p 27017:27017 mongo:6.0
```

Then run the setup script to seed with test data:
```bash
python test_data/setup_databases.py
```

**Alternative:** If Docker unavailable, install MySQL and MongoDB locally on your laptop/lab server, then run the same setup script.

---

## Ensuring Reproducibility

1. **Git Commit:** Before running benchmarks, commit all test data and note the Git commit hash
2. **Environment:** Set these before each benchmark run:
   ```bash
   export VIBEBENCH_SEED=42
   export VIBEBENCH_TIMEZONE=UTC
   ```
3. **Record Details:** In your results CSV, log:
   - Test data Git commit hash
   - Python version
   - System (laptop/server name)
   - Date/time
4. **Report:** When publishing results, state: "All benchmarks used test data from commit X, with environment Y, on date Z"

This simple approach is sufficient for research—readers can checkout the exact test data and reproduce your results.

---

## Maintaining Test Data

- **Keep test data in Git:** `test_data/` directory tracked with code
- **Document changes:** If you modify tasks mid-project, commit with message: "chore: update task A test data (more edge cases)"
- **Avoid deletion:** Never delete old test data; if running multiple rounds of benchmarks, document which commit hash was used for each round in your results log
- **Backup:** Git automatically backs up your test data; no additional versioning system needed for a research project

## Example Benchmark Run

When you run benchmarks and collect results, your results CSV should capture all **5 evaluation factors**:

```csv
model,task,attempt,language_supported,compile_status,compilation_warnings,functional_correctness,security_issues,security_mitigations,readability_score,comment_density,exec_time_ms,memory_mb,test_data_commit,python_version
gpt-4-turbo,A,1,yes,success,,1.0,0,[],3,0.15,45,12,a1b2c3d,3.11.8
gpt-4-turbo,B,1,yes,warning,"UnusedVariable at line 8",1.0,1,"[{fix: 'remove unused var'}]",5,0.08,120,18,a1b2c3d,3.11.8
claude-3-sonnet,A,1,yes,success,,1.0,0,[],2,0.22,38,11,a1b2c3d,3.11.8
```

This dataset covers all 5 required evaluation factors and allows computation of the **Best AI Per Task** final output.
