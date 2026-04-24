from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import csv
import sqlite3
from dotenv import load_dotenv
from orchestrator import orchestrator
from database import get_db_connection, init_db
from model_catalog import get_supported_models, is_supported_model

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
STRICT_MODEL_VALIDATION = os.getenv("STRICT_MODEL_VALIDATION", "true").lower() in {"1", "true", "yes"}

app = FastAPI(title="VibeBench API", description="Backend orchestrator for VibeBench")

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_database_status() -> dict[str, str]:
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "connected", "detail": "SQLite experiments database is reachable"}
    except sqlite3.Error as error:
        return {"status": "error", "detail": str(error)}

class BenchmarkRequest(BaseModel):
    task_id: str
    ai_model: str
    language: str
    code: str | None = None

@app.get("/")
def read_root():
    return {"status": "VibeBench Backend is running"}

@app.get("/api/health")
def health_check():
    print("DEBUG: Received request for /api/health")
    database_status = check_database_status()
    print(f"DEBUG: Database status: {database_status['status']}")

    return {
        "status": "ok",
        "backend": "running",
        "database": database_status,
        "frontend_origin": FRONTEND_ORIGIN,
        "ready": database_status["status"] == "connected",
    }


@app.get("/api/models")
def list_models():
    """Returns the configured AI models available for benchmarking."""
    print("DEBUG: Received request for /api/models")
    models = get_supported_models()
    print(f"DEBUG: Returning {len(models)} models")
    return {"models": models}

@app.post("/api/benchmark")
def run_benchmark(request: BenchmarkRequest):
    """
    Executes a single benchmark run
    """
    if STRICT_MODEL_VALIDATION and not is_supported_model(request.ai_model):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported model '{request.ai_model}'. "
                "Use /api/models to fetch available model IDs."
            ),
        )

    result = orchestrator.run_experiment(
        task_id=request.task_id, 
        ai_model=request.ai_model, 
        language=request.language, 
        code=request.code
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@app.get("/api/tasks/{task_id}/expected")
def get_task_expected_output(task_id: str):
    from tasks.evaluators import get_expected_output
    return get_expected_output(task_id)

@app.get("/api/results")
def get_results():
    """
    Fetches all experiments from the SQLite database
    """
    print("DEBUG: Received request for /api/results")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"DEBUG: Returning {len(rows)} experiment results")
    # Convert sqlite3.Row objects to standard dicts
    return [dict(row) for row in rows]

@app.get("/api/export/csv")
def export_csv():
    """
    Exports the results to a CSV file and returns it as a download.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No data to export")

    csv_path = "results.csv"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row)

    return FileResponse(
        path=csv_path,
        filename="vibebench_results.csv",
        media_type="text/csv"
    )
