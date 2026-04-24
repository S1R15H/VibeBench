import os
import re
import json
import zipfile
import csv
import hashlib
import logging
from datetime import date

logger = logging.getLogger(__name__)

MIN_LOGICAL_LINES = 30
MAX_ALLOWED_LINE_LENGTH = 120

RISKY_PATTERNS = {
    "python": [
        r"\beval\(",
        r"\bexec\(",
        r"subprocess\.(run|Popen)\([^\n]*shell\s*=\s*True",
        r"os\.system\(",
        r"pickle\.loads\(",
        r"hashlib\.(md5|sha1)\(",
    ],
    "javascript": [
        r"\beval\(",
        r"new\s+Function\(",
        r"child_process\.exec\(",
        r"md5",
        r"sha1",
    ],
    "php": [
        r"\beval\(",
        r"\bmd5\(",
        r"\bsha1\(",
        r"shell_exec\(",
        r"system\(",
    ],
    "bash": [
        r"\beval\s+",
        r"\bcurl\s+[^\n]*\|\s*bash",
    ],
}

def normalize_output(text: str) -> str:
    return text.strip().replace("\r\n", "\n")

def _task_data_path(task_id: str, filename: str) -> str:
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "test_data", f"task_{task_id.lower()}")
    )
    return os.path.join(base, filename)

def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)

def _load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()

def _extract_json_object(output: str):
    cleaned = normalize_output(output)
    if not cleaned:
        return None
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    for match in re.findall(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    return None

def _logical_code_lines(code: str, language: str) -> list[str]:
    lines = code.splitlines()
    logical = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
            continue
        logical.append(stripped)
    return logical

def _count_function_like_blocks(code: str, language: str) -> int:
    patterns = {
        "python": r"\bdef\s+\w+\s*\(",
        "javascript": r"\bfunction\s+\w*|=>",
        "php": r"\bfunction\s+\w+\s*\(",
        "bash": r"\w+\s*\(\s*\)\s*\{",
    }
    pattern = patterns.get(language, r"\{")
    return len(re.findall(pattern, code))

def _has_error_handling_construct(code: str, language: str) -> bool:
    markers = {
        "python": ("try:", "except"),
        "javascript": ("try", "catch"),
        "php": ("try", "catch"),
        "bash": ("set -e", "trap", "|| exit"),
    }
    return any(m in code for m in markers.get(language, []))

def _has_input_validation_construct(code: str, language: str) -> bool:
    markers = {
        "python": ("if not ", "raise ValueError"),
        "javascript": ("if (!", "throw new Error"),
        "php": ("if (!", "throw new"),
        "bash": ("if [[", "exit 1"),
    }
    return any(m in code for m in markers.get(language, []))

def evaluate_code_quality(code: str, language: str) -> dict:
    lang = language.lower()
    logical_lines = _logical_code_lines(code, lang)
    function_blocks = _count_function_like_blocks(code, lang)
    has_err = _has_error_handling_construct(code, lang)
    has_val = _has_input_validation_construct(code, lang)
    
    reasons = []
    if len(logical_lines) < MIN_LOGICAL_LINES:
        reasons.append(f"Short code ({len(logical_lines)} lines)")
    if function_blocks < 1:
        reasons.append("Missing modularity (no functions)")
    if not has_err:
        reasons.append("Missing error handling")
    if not has_val:
        reasons.append("Missing input validation")
        
    return {
        "passed": len(reasons) == 0,
        "reasons": reasons
    }

def verify_task_a(output: str, error: str) -> bool:
    expected = get_expected_output("A")
    actual = _extract_json_object(output)
    return actual == expected

def verify_task_b(output: str, error: str) -> bool:
    expected = get_expected_output("B")
    actual = _extract_json_object(output)
    if not isinstance(actual, dict): return False
    for k, v in expected.items():
        if k in ["thread_count", "worker_chunk_size"]: continue
        if actual.get(k) != v: return False
    return True

def verify_task_c(output: str, error: str, file_path: str = None) -> bool:
    if file_path is None: file_path = _task_data_path("c", "output.txt")
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def verify_task_d(output: str, error: str, file_path: str = None) -> bool:
    if file_path is None: file_path = _task_data_path("d", "output.json")
    try:
        with open(file_path, "r") as f:
            return isinstance(json.load(f), (dict, list))
    except: return False

def verify_task_e(output: str, error: str, zip_path: str = None) -> bool:
    if zip_path is None: zip_path = _task_data_path("e", "archive.zip")
    return zipfile.is_zipfile(zip_path) if os.path.exists(zip_path) else False

def verify_task_f(output: str, error: str) -> bool:
    return "id" in output.lower() or "row" in output.lower()

def verify_task_g(output: str, error: str) -> bool:
    return "objectid" in output.lower() or "{" in output

def verify_task_h(output: str, error: str) -> bool:
    return len(re.findall(r'[0-9a-fA-F]{32,}', output)) > 0

EVALUATORS = {
    "A": verify_task_a, "B": verify_task_b, "C": verify_task_c, "D": verify_task_d,
    "E": verify_task_e, "F": verify_task_f, "G": verify_task_g, "H": verify_task_h,
}

def evaluate_task(task_id: str, output: str, error: str, code: str = None, language: str = None) -> float:
    evaluator = EVALUATORS.get(task_id.upper())
    if not evaluator: return 0.0
    try:
        if not evaluator(output, error): return 0.0
        return 1.0
    except: return 0.0

def get_expected_output(task_id: str) -> dict:
    task_id = task_id.upper()
    try:
        if task_id == "A":
            input_path = _task_data_path("a", "input.txt")
            source = _load_text(input_path)
            rows = list(csv.DictReader(source.splitlines()))
            total_amount = round(sum(float(row["Amount"]) for row in rows), 2)
            max_order = max(rows, key=lambda row: float(row["Amount"]))["Order ID"]
            parsed_dates = [date.fromisoformat(row["Date"]) for row in rows]
            span_days = (max(parsed_dates) - min(parsed_dates)).days
            notes_with_commas = sum(1 for row in rows if "," in row["Notes"])
            return {
                "task": "A", "record_count": len(rows), "total_amount": total_amount,
                "max_order_id": max_order, "date_span_days": span_days, "notes_with_commas": notes_with_commas,
                "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            }
        if task_id == "B":
            data_path = _task_data_path("b", "data.json")
            entries = _load_json(data_path)
            total_value = sum(int(entry["value"]) for entry in entries)
            priority_totals = {}
            for entry in entries:
                p = entry["meta"]["priority"]
                priority_totals[p] = priority_totals.get(p, 0) + int(entry["value"])
            ranked = sorted(entries, key=lambda e: (-int(e["value"]), int(e["id"])))
            token_source = "|".join(f"{e['id']}:{e['value']}" for e in entries)
            return {
                "task": "B", "record_count": len(entries), "total_value": total_value,
                "priority_totals": priority_totals, "top3_ids_by_value": [int(e["id"]) for e in ranked[:3]],
                "integrity_token": hashlib.sha256(token_source.encode("utf-8")).hexdigest(),
            }
        return {"info": f"Expected output schema for Task {task_id} is dynamic/complex."}
    except Exception as e:
        return {"error": str(e)}