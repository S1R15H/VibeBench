import os
import sys
import time
import subprocess
import tempfile
import logging
import json
import shutil
from tasks.evaluators import evaluate_task, evaluate_code_quality
from scanners.security import get_security_analysis
from scanners.readability import analyze_readability
from database import store_experiment
from ollama_generator import generate_code_with_metadata, parse_output_payload
from model_catalog import get_model_config, is_supported_model

logger = logging.getLogger(__name__)


class ExperimentOrchestrator:
    def __init__(self):
        self.supported_langs = {
            "python": ".py",
            "javascript": ".js",
            "php": ".php",
            "bash": ".sh"
        }
        self.runtime_candidates = {
            "python": [sys.executable, "python3", "python"],
            "javascript": ["node", "nodejs"],
            "php": ["php", "php8.3", "php8.2", "php8.1", "php8.0"],
            "bash": ["bash", "sh"],
        }

    def _resolve_runtime_binary(self, language: str) -> str | None:
        for candidate in self.runtime_candidates.get(language, []):
            if shutil.which(candidate):
                return candidate
        return None

    def run_experiment(self, task_id: str, ai_model: str, language: str, code: str | None = None):
        """
        Executes the AI model's code, captures metrics, and stores the results.
        """
        lang = language.lower()

        if lang not in self.supported_langs:
            return {"error": f"Unsupported language: {language}"}

        extension = self.supported_langs[lang]

        if is_supported_model(ai_model):
            model_config = get_model_config(ai_model)
        else:
            model_config = {
                "name": ai_model,
                "model_id": ai_model,
            }

        code_source = "user_input"
        generation_warning = ""
        if code:
            generated_code = code
        else:
            generation_result = generate_code_with_metadata(task_id, ai_model, language)
            generated_code = generation_result.get("code", "")
            code_source = generation_result.get("source", "generation_failed")
            generation_warning = generation_result.get("warning", "")
            generation_error = generation_result.get("error", "")
            if not generated_code:
                return {
                    "error": (
                        "AI code generation failed. "
                        f"{generation_error or 'No code returned by model.'}"
                    )
                }

        with tempfile.NamedTemporaryFile(suffix=extension, mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(generated_code)
            file_path = temp_file.name

        try:
            readability_metrics = analyze_readability(generated_code, language)
            security_metrics = get_security_analysis(language, file_path)
            quality_gate = evaluate_code_quality(generated_code, language)
            execution_res = self._execute_code(file_path, language, task_id)
            execution_output = parse_output_payload(execution_res["stdout"])

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
                security_issues = 0
                security_details = []
                security_mitigations = []

            functional_correctness = 0.0
            if execution_res["compile_status"] != "failure":
                functional_correctness = evaluate_task(
                    task_id,
                    execution_res["stdout"],
                    execution_res["stderr"],
                    code=generated_code,
                    language=language,
                )

            from utils.scoring import (
                calculate_correctness_score,
                calculate_security_score,
                calculate_readability_score,
                format_score
            )
            
            # Normalize Scores (X / 10)
            corr_val, corr_max = calculate_correctness_score(functional_correctness == 1.0, execution_res["compile_status"])
            sec_val, sec_max = calculate_security_score(security_issues, security_details)
            read_val, read_max = calculate_readability_score(readability_metrics.get("readability_score", 1.0), readability_metrics.get("comment_density", 0.0))

            quality_gate_passed = quality_gate["passed"] and execution_res["compile_status"] == "success"

            notes = json.dumps({
                "quality_gate": {
                    "passed": quality_gate_passed,
                    "reasons": quality_gate["reasons"] if not quality_gate_passed else []
                },
                "security_scan_status": security_metrics.get("status", "unknown"),
                "code_source": code_source,
                "generation_warning": generation_warning,
                "scores": {
                    "correctness": format_score(corr_val, corr_max),
                    "security": format_score(sec_val, sec_max),
                    "readability": format_score(read_val, read_max)
                }
            })

            exp_id = store_experiment(
                ai_model=model_config["name"],
                task_id=task_id,
                language=language,
                language_supported="yes",
                code=generated_code,
                compile_status=execution_res["compile_status"],
                compilation_errors=execution_res["stderr"] if execution_res["compile_status"] == "failure" else "",
                compilation_warnings=execution_res["stderr"] if execution_res["compile_status"] == "warning" else "",
                execution_output=execution_output,
                functional_correctness=functional_correctness,
                security_issues=security_issues,
                security_details=security_details,
                security_mitigations=security_mitigations,
                readability_score=readability_metrics["readability_score"],
                comment_density=readability_metrics["comment_density"],
                execution_time_ms=execution_res["execution_time_ms"],
                memory_used_mb=0,
                notes=notes,
                model_id=model_config["model_id"],
                model_region=model_config.get("region", "N/A")
            )

            return {
                "id": exp_id,
                "status": "success",
                "compile_status": execution_res["compile_status"],
                "correctness": functional_correctness,
                "security_issues": security_issues,
                "security_scan_status": security_metrics["status"],
                "quality_gate": quality_gate_passed,
                "quality_gate_reasons": quality_gate["reasons"] if not quality_gate_passed else [],
                "readability_score": readability_metrics["readability_score"],
                "comment_density": readability_metrics["comment_density"],
                "execution_time_ms": execution_res["execution_time_ms"],
                "ai_model": model_config["name"],
                "model_id": model_config["model_id"],
                "model_region": model_config.get("region", "N/A"),
                "code_source": code_source,
                "generation_warning": generation_warning,
                "code": generated_code,
                "stdout": execution_res["stdout"],
                "stderr": execution_res["stderr"],
                "execution_output": execution_output,
                "scores": {
                    "correctness": format_score(corr_val, corr_max),
                    "security": format_score(sec_val, sec_max),
                    "readability": format_score(read_val, read_max)
                }
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
        if lang not in self.supported_langs:
            return {
                "compile_status": "failure",
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "execution_time_ms": 0
            }

        runtime_binary = self._resolve_runtime_binary(lang)
        if runtime_binary is None:
            expected_runtimes = ", ".join(self.runtime_candidates.get(lang, []))
            return {
                "compile_status": "failure",
                "stdout": "",
                "stderr": (
                    f"Runtime not available for {language}. Tried: {expected_runtimes}. "
                    "Install the interpreter or run the backend inside the VibeBench Docker image."
                ),
                "execution_time_ms": 0,
            }

        cmd = [runtime_binary, file_path]

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
        except FileNotFoundError as e:
            missing_runtime = str(e).split(":")[-1].strip().strip("'")
            return {
                "compile_status": "failure",
                "stdout": "",
                "stderr": (
                    f"Runtime not available: {missing_runtime}. "
                    f"Install the required interpreter for {language} or run the backend in Docker."
                ),
                "execution_time_ms": 0,
            }


orchestrator = ExperimentOrchestrator()