from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import csv
from dotenv import load_dotenv
from orchestrator import orchestrator
from database import get_db_connection

load_dotenv()

app = FastAPI(title="VibeBench API", description="Backend orchestrator for VibeBench")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BenchmarkRequest(BaseModel):
    task_id: str
    ai_model: str
    language: str
    code: str

@app.get("/")
def read_root():
    return {"status": "VibeBench Backend is running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/benchmark")
def run_benchmark(request: BenchmarkRequest):
    """
    Executes a single benchmark run
    """
    result = orchestrator.run_experiment(
        task_id=request.task_id, 
        ai_model=request.ai_model, 
        language=request.language, 
        code=request.code
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@app.get("/api/results")
def get_results():
    """
    Fetches all experiments from the SQLite database
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to standard dicts
    return [dict(row) for row in rows]

@app.get("/api/export/csv")
def export_csv():
    """
    Exports the results to a CSV file in the backend folder
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"status": "No data to export"}

    csv_path = "results.csv"
    with open(csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row)
            
    return {"status": "success", "file": csv_path}
