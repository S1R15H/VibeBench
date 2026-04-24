import sqlite3
import os
import json
from datetime import datetime

DB_PATH = 'experiments.db'

EXPERIMENT_COLUMNS = [
    "id",
    "timestamp",
    "ai_model",
    "model_id",
    "model_region",
    "task_id",
    "language",
    "language_supported",
    "code",
    "compile_status",
    "compilation_errors",
    "compilation_warnings",
    "execution_output",
    "functional_correctness",
    "security_issues",
    "security_details",
    "security_mitigations",
    "readability_score",
    "comment_density",
    "execution_time_ms",
    "memory_used_mb",
    "notes",
]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ai_model TEXT NOT NULL,
            model_id TEXT,
            model_region TEXT,
            task_id TEXT NOT NULL,
            language TEXT NOT NULL,
            language_supported TEXT DEFAULT 'yes',
            code TEXT NOT NULL,
            compile_status TEXT NOT NULL,
            compilation_errors TEXT,
            compilation_warnings TEXT,
            execution_output TEXT,
            functional_correctness REAL DEFAULT 0,
            security_issues INTEGER DEFAULT 0,
            security_details TEXT,
            security_mitigations TEXT,
            readability_score REAL,
            comment_density REAL,
            execution_time_ms INTEGER,
            memory_used_mb INTEGER,
            notes TEXT
        )
    ''')

    cursor.execute("PRAGMA table_info(experiments)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    migrations = [
        ("model_id", "TEXT"),
        ("model_region", "TEXT"),
        ("execution_output", "TEXT"),
    ]
    for column_name, column_type in migrations:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE experiments ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()

def store_experiment(
    ai_model: str, task_id: str, language: str, language_supported: str,
    code: str, compile_status: str, compilation_errors: str,
    compilation_warnings: str, execution_output: str, functional_correctness: float,
    security_issues: int, security_details: list, security_mitigations: list,
    readability_score: float, comment_density: float,
    execution_time_ms: int, memory_used_mb: int, notes: str = "",
    model_id: str = "", model_region: str = ""
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO experiments (
            timestamp, ai_model, model_id, model_region, task_id, language, language_supported,
            code, compile_status, compilation_errors, compilation_warnings, execution_output,
            functional_correctness, security_issues, security_details,
            security_mitigations, readability_score, comment_density,
            execution_time_ms, memory_used_mb, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(), ai_model, model_id, model_region, task_id, language, language_supported,
        code, compile_status, compilation_errors, compilation_warnings, json.dumps(execution_output),
        functional_correctness, security_issues, json.dumps(security_details),
        json.dumps(security_mitigations), readability_score, comment_density,
        execution_time_ms, memory_used_mb, notes
    ))
    conn.commit()
    conn.close()
    return cursor.lastrowid

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
