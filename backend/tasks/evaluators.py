import os
import re
import json
import zipfile


def normalize_output(text: str) -> str:
    return text.strip().replace("\r\n", "\n")


def _task_data_path(task_id: str, filename: str) -> str:
    """
    Returns the absolute path to a file inside the task-specific test_data folder.
    e.g. _task_data_path("c", "output.txt")
      -> /path/to/VibeBench/test_data/task_c/output.txt
    """
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "test_data", f"task_{task_id.lower()}")
    )
    return os.path.join(base, filename)


def verify_task_a(output: str, error: str) -> bool:
    """
    Task A: Read and print a text file.
    Expected output must exactly match the contents of input.txt.
    """
    expected = "Hello VibeBench!\nThis is a test file for Task A."
    return normalize_output(output) == normalize_output(expected)


def verify_task_b(output: str, error: str) -> bool:
    """
    Task B: Parse and print a list of items.
    All five items must appear, each on its own line, in any order.
    """
    required_keywords = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    cleaned = normalize_output(output)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return all(any(kw == line or kw in line.split() for line in lines) for kw in required_keywords)


def verify_task_c(output: str, error: str, file_path: str = None) -> bool:
    """
    Task C: Write specific content to output.txt.
    The file must exist, be non-empty, and not contain a traceback.
    """
    if file_path is None:
        file_path = _task_data_path("c", "output.txt")

    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return False

    error_indicators = ["Traceback (most recent call last)", "Error:", "Exception:"]
    if any(indicator in content for indicator in error_indicators):
        return False

    return True


def verify_task_d(output: str, error: str, file_path: str = None) -> bool:
    """
    Task D: Produce a valid, non-empty JSON file.
    Must be a list or dict with at least one entry.
    """
    if file_path is None:
        file_path = _task_data_path("d", "output.json")

    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, (list, dict)):
            return False
        if len(data) == 0:
            return False

        if isinstance(data, list):
            return any(item not in (None, "", 0, False) for item in data)

        return True

    except json.JSONDecodeError:
        return False


def verify_task_e(output: str, error: str, zip_path: str = None) -> bool:
    """
    Task E: Create a valid zip archive with at least one file inside.
    """
    if zip_path is None:
        zip_path = _task_data_path("e", "archive.zip")

    if not os.path.exists(zip_path):
        return False

    if not zipfile.is_zipfile(zip_path):
        return False

    with zipfile.ZipFile(zip_path, "r") as zf:
        return len(zf.namelist()) > 0


def verify_task_f(output: str, error: str) -> bool:
    """
    Task F: Query a MySQL database and print results.
    Requires actual structured data rows, not just any string containing 'row' or 'id'.
    """
    cleaned = normalize_output(output)

    if not cleaned:
        return False

    error_indicators = ["error", "traceback", "exception", "denied", "refused", "not found"]
    lower = cleaned.lower()
    if any(ind in lower for ind in error_indicators):
        return False

    data_line_pattern = re.compile(r'(\d+|\|.+\||[\w]+\s*[=:]\s*\S+)')
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return any(data_line_pattern.search(line) for line in lines)


def verify_task_g(output: str, error: str) -> bool:
    """
    Task G: Query a MongoDB collection and print documents.
    Requires output that looks like actual document data.
    """
    cleaned = normalize_output(output)

    if not cleaned:
        return False

    lower = cleaned.lower()

    error_indicators = ["error", "traceback", "exception", "refused", "not found"]
    if any(ind in lower for ind in error_indicators):
        return False

    objectid_pattern = re.compile(r"objectid\s*\(", re.IGNORECASE)
    json_doc_pattern = re.compile(r'\{[^}]{3,}\}')
    id_field_pattern = re.compile(r'_id\s*[=:]\s*\S+', re.IGNORECASE)

    return bool(
        objectid_pattern.search(cleaned)
        or json_doc_pattern.search(cleaned)
        or id_field_pattern.search(cleaned)
    )


def verify_task_h(output: str, error: str) -> bool:
    """
    Task H: Hash a value and print the result.
    Requires a hex digest (32+ hex characters) in the output.
    """
    cleaned = normalize_output(output)

    if not cleaned:
        return False

    hex_pattern = re.compile(r'[0-9a-fA-F]{32,}')
    return bool(hex_pattern.search(cleaned))


EVALUATORS = {
    "A": verify_task_a,
    "B": verify_task_b,
    "C": verify_task_c,
    "D": verify_task_d,
    "E": verify_task_e,
    "F": verify_task_f,
    "G": verify_task_g,
    "H": verify_task_h,
}


def evaluate_task(task_id: str, output: str, error: str) -> float:
    evaluator = EVALUATORS.get(task_id)

    if evaluator is None:
        return 0.0

    try:
        return 1.0 if evaluator(output, error) else 0.0
    except Exception as e:
        print(f"Evaluator error for task {task_id}: {e}")
        return 0.0