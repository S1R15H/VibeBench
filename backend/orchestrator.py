import os
import sys
import time
import subprocess
import tempfile
import logging
from tasks.evaluators import evaluate_task
from scanners.security import get_security_analysis
from scanners.readability import analyze_readability
from database import store_experiment

logger = logging.getLogger(__name__)


class ExperimentOrchestrator:
    def __init__(self):
        self.supported_langs = {
            "python": ".py",
            "javascript": ".js",
            "js": ".js",
            "node": ".js",
            "php": ".php",
            "bash": ".sh"
        }

    def run_experiment(self, task_id: str, ai_model: str, language: str, code: str):
        """
        Executes the AI model's code, captures metrics, and stores the results.
        """
        lang = language.lower()

        if lang not in self.supported_langs:
            return {"error": f"Unsupported language: {language}"}

        extension = self.supported_langs[lang]

        with tempfile.NamedTemporaryFile(suffix=extension, mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code)
            file_path = temp_file.name

        try:
            readability_metrics = analyze_readability(code, language)
            security_metrics = get_security_analysis(language, file_path)
            execution_res = self._execute_code(file_path, language, task_id)

            # Guard against Bandit errors/skips so we don't record 0 as a clean result.
            if security_metrics["status"] == "ok":
                security_issues = security_metrics["issues"]
                security_details = security_metrics["details"]
                security_mitigations = security_metrics["mitigations"]
            else:
                logger.warning(
                    "Security scan did not complete for task %s (status=%s, reason=%s)",
                    task_id,
                    security_metrics["status"],
                    security_metrics.get("reason", "unknown"),
                )
                security_issues = None
                security_details = []
                security_mitigations = []

            functional_correctness = 0.0
            if execution_res["compile_status"] != "failure":
                functional_correctness = evaluate_task(
                    task_id,
                    execution_res["stdout"],
                    execution_res["stderr"]
                )

            exp_id = store_experiment(
                ai_model=ai_model,
                task_id=task_id,
                language=language,
                language_supported="yes",
                code=code,
                compile_status=execution_res["compile_status"],
                compilation_errors=execution_res["stderr"] if execution_res["compile_status"] == "failure" else "",
                compilation_warnings=execution_res["stderr"] if execution_res["compile_status"] == "warning" else "",
                functional_correctness=functional_correctness,
                security_issues=security_issues,
                security_details=security_details,
                security_mitigations=security_mitigations,
                readability_score=readability_metrics["readability_score"],
                comment_density=readability_metrics["comment_density"],
                execution_time_ms=execution_res["execution_time_ms"],
                memory_used_mb=0
            )

            return {
                "id": exp_id,
                "status": "success",
                "compile_status": execution_res["compile_status"],
                "correctness": functional_correctness,
                "security_issues": security_issues,
                "security_scan_status": security_metrics["status"],
            }

        except Exception as e:
            logger.error(f"Experiment pipeline crash: {e}")
            return {"error": str(e)}

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _execute_code(self, file_path: str, language: str, task_id: str) -> dict:
        """Runs the file using subprocess and captures output, stderr, and execution time."""
        lang = language.lower()
        cmd = []

        if lang == "python":
            cmd = [sys.executable, file_path]
        elif lang in ["javascript", "js", "node"]:
            cmd = ["node", file_path]
        elif lang == "php":
            cmd = ["php", file_path]
        elif lang == "bash":
            cmd = ["bash", file_path]
        else:
            return {
                "compile_status": "failure",
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "execution_time_ms": 0
            }

        # Use task-specific subfolder as cwd so code can find its test data files
        # e.g. task_id="A" -> test_data/task_a/
        task_data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "test_data", f"task_{task_id.lower()}")
        )

        # Fall back to the root test_data folder if no task subfolder exists
        if not os.path.isdir(task_data_dir):
            task_data_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "test_data")
            )
            logger.warning("No task-specific folder for task %s, falling back to test_data/", task_id)

        start_time = time.perf_counter()

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=task_data_dir
            )

            end_time = time.perf_counter()
            exec_time_ms = int((end_time - start_time) * 1000)

            if res.returncode != 0:
                compile_status = "failure"
            elif res.stderr and len(res.stderr.strip()) > 0:
                compile_status = "warning"
            else:
                compile_status = "success"

            return {
                "compile_status": compile_status,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "execution_time_ms": exec_time_ms
            }

        except subprocess.TimeoutExpired:
            return {
                "compile_status": "failure",
                "stdout": "",
                "stderr": "Execution timed out (60s limit).",
                "execution_time_ms": 60000
            }


orchestrator = ExperimentOrchestrator()