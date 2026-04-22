import os
import json
import zipfile


def normalize_output(text: str) -> str:
    return text.strip().replace("\r\n", "\n")


def verify_task_a(output: str, error: str) -> bool:
    expected = "Hello VibeBench!\nThis is a test file for Task A."
    cleaned_output = output.strip().replace("\r\n", "\n")
    cleaned_expected = expected.strip().replace("\r\n", "\n")
    print("DEBUG OUTPUT:", repr(cleaned_output))
    print("DEBUG EXPECTED:", repr(cleaned_expected))
    return cleaned_output == cleaned_expected


def verify_task_b(output: str, error: str) -> bool:
    required_keywords = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    cleaned = normalize_output(output)
    return all(kw in cleaned for kw in required_keywords)


def verify_task_c(output: str, error: str, file_path: str = "output.txt") -> bool:
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return len(content.strip()) > 0


def verify_task_d(output: str, error: str, file_path: str = "output.json") -> bool:
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return isinstance(data, (list, dict)) and len(data) > 0
    except json.JSONDecodeError:
        return False


def verify_task_e(output: str, error: str, zip_path: str = "archive.zip") -> bool:
    if not os.path.exists(zip_path):
        return False

    return zipfile.is_zipfile(zip_path)


def verify_task_f(output: str, error: str) -> bool:
    cleaned = normalize_output(output).lower()
    return len(cleaned) > 0 and ("row" in cleaned or "id" in cleaned)


def verify_task_g(output: str, error: str) -> bool:
    cleaned = normalize_output(output).lower()
    return len(cleaned) > 0 and ("document" in cleaned or "_id" in cleaned)


def verify_task_h(output: str, error: str) -> bool:
    cleaned = normalize_output(output).lower()
    return "hash" in cleaned or "success" in cleaned or "true" in cleaned


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