import os
import json

def verify_task_a(output: str, error: str) -> bool:
    """Verify that the output contains the contents of input.txt"""
    expected = "Hello VibeBench!\nThis is a test file for Task A."
    return expected in output

def verify_task_b(output: str, error: str) -> bool:
    """Verify multi-threaded JSON read output"""
    # Just check if it successfully parsed and printed the JSON contents somehow
    required_keywords = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    return all(kw in output for kw in required_keywords)

def verify_task_c(output: str, error: str, file_path: str = "output.txt") -> bool:
    """Verify that a text file was created with some content"""
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r') as f:
        content = f.read()
    return len(content.strip()) > 0

def verify_task_d(output: str, error: str, file_path: str = "output.json") -> bool:
    """Verify that a JSON file was written via multiple threads"""
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return isinstance(data, (list, dict)) and len(data) > 0
    except json.JSONDecodeError:
        return False

def verify_task_e(output: str, error: str, zip_path: str = "archive.zip") -> bool:
    """Verify that a zip archive was produced"""
    import zipfile
    if not os.path.exists(zip_path):
        return False
    return zipfile.is_zipfile(zip_path)

def verify_task_f(output: str, error: str) -> bool:
    """Verify MySQL retrieval output"""
    # Assuming the code prints the retrieved record
    return "row" in output.lower() or "id" in output.lower() and len(output.strip()) > 0

def verify_task_g(output: str, error: str) -> bool:
    """Verify MongoDB retrieval output"""
    return "document" in output.lower() or "_id" in output.lower() and len(output.strip()) > 0

def verify_task_h(output: str, error: str) -> bool:
    """Verify Password authentication logic output"""
    # Expecting output to show a hash or successful auth message
    return "hash" in output.lower() or "success" in output.lower() or "true" in output.lower()

EVALUATORS = {
    "A": verify_task_a,
    "B": verify_task_b,
    "C": verify_task_c,
    "D": verify_task_d,
    "E": verify_task_e,
    "F": verify_task_f,
    "G": verify_task_g,
    "H": verify_task_h
}
