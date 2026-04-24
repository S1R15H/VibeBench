from __future__ import annotations

import hashlib
import json
import os
import re
import textwrap
from typing import Dict

import requests
from model_catalog import get_model_config, is_supported_model


TASK_DESCRIPTIONS: Dict[str, str] = {
    "A": (
        "Build a production-style CSV ingestion feature (target 35-70 LOC) with "
        "helper functions, input validation, and explicit error handling. Read "
        "input.txt as CSV and print one JSON object with exact keys: "
        "task, record_count, total_amount, max_order_id, date_span_days, "
        "notes_with_commas, input_sha256. total_amount must be numeric with "
        "2 decimal precision."
    ),
    "B": (
        "Build a concurrent data-aggregation feature (target 35-90 LOC) using "
        "clean structure, validation, and robust exception handling. Read data.json "
        "and print one JSON object with exact keys: task, "
        "record_count, total_value, priority_totals, top3_ids_by_value, "
        "integrity_token, thread_count, worker_chunk_size. thread_count must "
        "be >= 2 and worker_chunk_size > 0."
    ),
    "C": (
        "Implement a report-generation module (target 30-70 LOC) with reusable "
        "functions, validation, and error paths. Read input.json and write output.txt as a deterministic report with "
        "ranked services, totals, AVG_UPTIME, and SIGNATURE line. Also print "
        "WRITE_OK:<signature>."
    ),
    "D": (
        "Implement an event analytics feature (target 35-80 LOC) with modular "
        "transformation helpers and defensive checks. Read input.json and write "
        "output.json with exact keys: task, "
        "event_count, users, actions, slow_event_ids, checksum. Also print "
        "JSON_OK:<checksum_prefix>."
    ),
    "E": (
        "Implement a secure packaging feature (target 30-70 LOC) with explicit "
        "path validation and failure handling. Create archive.zip that contains exactly sample.txt and manifest.json. "
        "manifest.json must include task, input_file, line_count, byte_size, "
        "input_sha256 for sample.txt. Also print ARCHIVE_OK:<sha_prefix>."
    ),
    "F": (
        "Implement a data-access style query service (target 35-80 LOC) with "
        "filter/sort helper functions and validation. Read employees.json and execute the hardcoded SQL-style filter: salary "
        ">= 90000 and department IN (Engineering, Security), sorted by salary "
        "DESC then id ASC. Print one JSON object with task, query, row_count, "
        "rows, avg_salary, salary_sum."
    ),
    "G": (
        "Implement a document-query feature (target 35-80 LOC) with modular "
        "query/filter/projection steps and safe guards. Read products.json and execute the hardcoded Mongo-style filter: "
        "category=Electronics, stock.warehouse>=10, tags contains featured. "
        "Sort by price DESC then _id ASC. Print one JSON object with task, "
        "query, document_count, documents, inventory_value, checksum."
    ),
    "H": (
        "Implement an authentication utility (target 35-90 LOC) using modern "
        "security practices, validation, and clear helper abstractions. Read auth_input.json and compute PBKDF2-HMAC-SHA256 using password, "
        "salt_hex, and iterations. Print one JSON object with exact keys: "
        "task, username, algorithm, iterations, salt_hex, password_hash, "
        "verify_correct, verify_incorrect. Never print plaintext passwords."
    ),
}

LANGUAGE_HINTS: Dict[str, str] = {
    "python": "Python 3.12",
    "javascript": "Node.js JavaScript",
    "js": "Node.js JavaScript",
    "node": "Node.js JavaScript",
    "php": "PHP 8+",
    "bash": "Bash",
}


def build_generation_prompt(task_id: str, language: str) -> str:
    task_description = TASK_DESCRIPTIONS.get(task_id.upper(), "Implement the benchmark task.")
    language_hint = LANGUAGE_HINTS.get(language.lower(), language)

    return textwrap.dedent(
        f"""
        You are generating source code for VibeBench benchmark task {task_id}.
        Return only executable {language_hint} code.
        No markdown fences, no explanations, no bullet points, no preamble.
        The code must be ready to run in the benchmark sandbox.

        Task requirements:
        {task_description}

        Runtime expectations:
        - Use the current working directory for task files.
        - Prefer deterministic output.
        - Write feature-quality code with modular helper functions (at least 30 logical lines).
        """
    ).strip()


def extract_code(text: str) -> str:
    """Extract code from response, removing markdown fences if present."""
    text = text.strip()
    
    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Try to find the closing fence
        start_idx = 0
        if lines[0].startswith("```"):
            start_idx = 1
            # Skip language identifier if present
            if start_idx < len(lines):
                start_idx = 1
        
        # Find end fence
        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            if lines[i].strip().startswith("```"):
                end_idx = i
                break
        
        text = "\n".join(lines[start_idx:end_idx]).strip()
    
    return text


def normalize_generated_code(code: str) -> str:
    """Normalize code by removing extra whitespace and comments if needed."""
    lines = code.split("\n")
    # Remove leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def parse_output_payload(output: str) -> dict:
    """Parse structured output from code execution."""
    try:
        if "JSON_OK:" in output:
            parts = output.split("JSON_OK:")
            if len(parts) > 1:
                checksum = parts[1].strip().split()[0]
                return {"status": "parsed", "checksum": checksum}
        
        if "WRITE_OK:" in output:
            parts = output.split("WRITE_OK:")
            if len(parts) > 1:
                sig = parts[1].strip().split()[0]
                return {"status": "parsed", "signature": sig}
        
        if "ARCHIVE_OK:" in output:
            parts = output.split("ARCHIVE_OK:")
            if len(parts) > 1:
                sha = parts[1].strip().split()[0]
                return {"status": "parsed", "archive_sha": sha}
        
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {"status": "parsed", "data": parsed}
        
        return {"status": "unparsed", "raw": output}
    except Exception as e:
        return {"status": "error", "error_detail": str(e)}


def generate_code_with_metadata(task_id: str, model_key: str, language: str) -> dict:
    """Generate code using Ollama Cloud API."""
    try:
        model_config = get_model_config(model_key)
        model_id = model_config.get("model_id")
        
        prompt = build_generation_prompt(task_id, language)
        
        # Ollama Cloud API Key
        ollama_api_key = os.getenv("OLLAMA_API_KEY", "").strip()
        
        if not ollama_api_key:
            return {
                "code": "",
                "source": "generation_failed",
                "warning": None,
                "error": "OLLAMA_API_KEY not set in environment",
            }
        
        try:
            # Call Ollama Cloud API (Native /api/chat endpoint on api.ollama.com)
            response = requests.post(
                "https://api.ollama.com/api/chat",
                headers={
                    "Authorization": f"Bearer {ollama_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=180,
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Parse native Ollama response: response_data["message"]["content"]
                if "message" in response_data and "content" in response_data["message"]:
                    generated_text = response_data["message"]["content"]
                    code = extract_code(generated_text)
                    code = normalize_generated_code(code)
                    
                    if code:
                        return {
                            "code": code,
                            "source": "ollama_cloud",
                            "warning": None,
                            "error": None,
                        }
                    else:
                        return {"code": "", "source": "generation_failed", "warning": None, "error": "Ollama response did not contain code"}
            else:
                return {"code": "", "source": "generation_failed", "warning": None, "error": f"Ollama API error: {response.status_code}"}
        
        except requests.exceptions.RequestException as exc:
            return {"code": "", "source": "generation_failed", "warning": None, "error": f"Ollama connection failed: {exc}"}
    
    except Exception as exc:
        return {"code": "", "source": "generation_failed", "warning": None, "error": f"Ollama generation failed: {exc}"}
