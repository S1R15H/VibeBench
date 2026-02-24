import os
import time
import subprocess
import tempfile
import logging
from tasks.evaluators import EVALUATORS
from scanners.security import get_security_analysis
from scanners.readability import analyze_readability
from database import store_experiment

logger = logging.getLogger(__name__)

class ExperimentOrchestrator:
    def __init__(self):
        self.supported_langs = {"python": ".py", "javascript": ".js", "php": ".php", "bash": ".sh"}

    def run_experiment(self, task_id: str, ai_model: str, language: str, code: str):
        """
        Executes the AI model's code, captures metrics, and stores the results.
        """
        if language.lower() not in self.supported_langs:
            return {"error": f"Unsupported language: {language}"}

        extension = self.supported_langs[language.lower()]
        
        # 1. Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=extension, mode='w', delete=False) as temp_file:
            temp_file.write(code)
            file_path = temp_file.name

        try:
            # 2. Extract Readability metrics (STATIC)
            readability_metrics = analyze_readability(code, language)
            
            # 3. Extract Security vulnerabilities & mitigations (STATIC)
            security_metrics = get_security_analysis(language, file_path)
            
            # 4. Execute the code safely (DYNAMIC)
            execution_res = self._execute_code(file_path, language)
            
            # 5. Evaluate logical correctness 
            functional_correctness = 0.0
            if execution_res["compile_status"] != "failure":
                evaluator = EVALUATORS.get(task_id)
                if evaluator:
                    passed = evaluator(execution_res["stdout"], execution_res["stderr"])
                    functional_correctness = 1.0 if passed else 0.0

            # 6. Save to database
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
                security_issues=security_metrics["issues"],
                security_details=security_metrics["details"],
                security_mitigations=security_metrics["mitigations"],
                readability_score=readability_metrics["readability_score"],
                comment_density=readability_metrics["comment_density"],
                execution_time_ms=execution_res["execution_time_ms"],
                memory_used_mb=0  # Could be captured explicitly via resource module
            )

            return {
                "id": exp_id,
                "status": "success",
                "compile_status": execution_res["compile_status"],
                "correctness": functional_correctness,
                "security_issues": security_metrics["issues"]
            }

        except Exception as e:
            logger.error(f"Experiment pipeline crash: {e}")
            return {"error": str(e)}
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _execute_code(self, file_path: str, language: str) -> dict:
        """Runs the file using subprocess and captures output, stderr, and execution time"""
        cmd = []
        if language.lower() == "python":
            cmd = ["python", file_path]
        elif language.lower() in ["javascript", "js", "node"]:
            cmd = ["node", file_path]
        elif language.lower() == "php":
            cmd = ["php", file_path]

        start_time = time.perf_counter()
        
        try:
            # In a full version, we'd use Docker here instead of straight subprocess.
            # Timeout is strictly enforced to 60 seconds.
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            end_time = time.perf_counter()
            exec_time_ms = int((end_time - start_time) * 1000)

            compile_status = "success"
            
            # Simple heuristic for errors vs warnings via returncode and stderr
            if res.returncode != 0:
                compile_status = "failure"
            elif res.stderr and len(res.stderr.strip()) > 0:
                compile_status = "warning"

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
