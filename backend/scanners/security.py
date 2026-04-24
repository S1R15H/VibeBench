import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

MITIGATIONS = {
    "B102": "Avoid using exec(); it can execute arbitrary code and is a common attack vector.",
    "B105": "Avoid hardcoded passwords; use environment variables or a secrets manager.",
    "B303": "MD5 and SHA1 are cryptographically broken; use hashlib.sha256 or stronger.",
    "B307": "eval() executes arbitrary code; avoid it or use safe literal parsing.",
    "B602": "subprocess with shell=True is vulnerable to shell injection; use shell=False and argument lists.",
    "B608": "String-built SQL can lead to injection; use parameterized queries.",
    "SHELLCHECK_SC2086": "Double-quote variable expansions to prevent globbing and word splitting.",
    "SHELLCHECK_SC2046": "Quote command substitutions to avoid word splitting issues.",
    "SHELLCHECK_SC2164": "Check cd failures explicitly (or use strict mode and error handling).",
    "JS_EVAL": "Avoid eval/new Function; use explicit parsing and bounded control flow.",
    "JS_EXEC": "Avoid child_process.exec with user-influenced values; use execFile/spawn with validated args.",
    "JS_WEAK_HASH": "Avoid MD5/SHA1 for security-sensitive logic; use modern primitives.",
    "JS_HARDCODED_SECRET": "Do not hardcode secrets; load from environment or secure secret store.",
    "PHP_EVAL": "Avoid eval in PHP; it can execute untrusted code paths.",
    "PHP_EXEC": "Avoid shell/system execution unless strictly validated and sandboxed.",
    "PHP_WEAK_HASH": "Avoid md5/sha1 for security-sensitive uses; use password_hash or stronger algorithms.",
    "PHP_HARDCODED_SECRET": "Do not hardcode secrets in source code.",
    "PY_EVAL": "Avoid eval/exec in Python code paths processing external input.",
    "PY_WEAK_HASH": "Avoid MD5/SHA1 for security-sensitive hashing.",
    "PY_SQL_STRING_BUILD": "Avoid building SQL with string concatenation; use parameterized queries.",
    "PY_SHELL_TRUE": "Avoid subprocess shell=True; pass argument lists and keep shell=False.",
}

PYTHON_RULES = [
    ("PY_EVAL", "HIGH", r"\b(eval|exec)\s*\("),
    ("PY_SHELL_TRUE", "HIGH", r"subprocess\.(run|Popen|call|check_output)\([^\n]*shell\s*=\s*True"),
    ("PY_WEAK_HASH", "MEDIUM", r"hashlib\.(md5|sha1)\s*\("),
    ("PY_SQL_STRING_BUILD", "MEDIUM", r"(?i)\b(select|insert|update|delete)\b.*(%s|\+|\.format\()"),
]

JS_RULES = [
    ("JS_EVAL", "HIGH", r"\beval\(|\bnew\s+Function\("),
    (
        "JS_EXEC",
        "HIGH",
        r"child_process\.(exec|execSync)\(|\brequire\(['\"]child_process['\"]\)\.exec|\bexec(Sync)?\s*\(",
    ),
    ("JS_WEAK_HASH", "MEDIUM", r"\b(md5|sha1)\b|createHash\(\s*['\"](md5|sha1)['\"]"),
    (
        "JS_HARDCODED_SECRET",
        "MEDIUM",
        r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}['\"]",
    ),
]

PHP_RULES = [
    ("PHP_EVAL", "HIGH", r"\beval\s*\("),
    ("PHP_EXEC", "HIGH", r"\b(shell_exec|system|exec|passthru)\s*\("),
    ("PHP_WEAK_HASH", "MEDIUM", r"\b(md5|sha1)\s*\("),
    (
        "PHP_HARDCODED_SECRET",
        "MEDIUM",
        r"(?i)(password|secret|token|api[_-]?key)\s*=>\s*['\"][^'\"]{6,}['\"]",
    ),
]


def _make_error_result(reason: str) -> dict:
    return {
        "status": "error",
        "reason": reason,
        "issues": 0,
        "details": [],
        "mitigations": [],
        "engine": "none",
    }


def _make_skipped_result(reason: str) -> dict:
    return {
        "status": "skipped",
        "reason": reason,
        "issues": 0,
        "details": [],
        "mitigations": [],
        "engine": "none",
    }


def _normalized_language(language: str) -> str:
    lang = language.lower().strip()
    if lang in {"js", "node"}:
        return "javascript"
    if lang in {"sh", "shell"}:
        return "bash"
    return lang


def _severity_confidence_passes(
    severity: str,
    confidence: str,
    min_severity: str,
    min_confidence: str,
) -> bool:
    sev_rank = SEVERITY_RANK.get(severity.upper(), 0)
    conf_rank = SEVERITY_RANK.get(confidence.upper(), 0)
    min_sev_rank = SEVERITY_RANK.get(min_severity.upper(), 1)
    min_conf_rank = SEVERITY_RANK.get(min_confidence.upper(), 1)
    return sev_rank >= min_sev_rank and conf_rank >= min_conf_rank


def _run_bandit(
    file_path: str,
    min_severity: str,
    min_confidence: str,
    timeout: int,
) -> dict:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return _make_error_result(f"File does not exist: {file_path}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _make_error_result(f"Bandit timed out after {timeout}s")
    except Exception as exc:
        return _make_error_result(f"Bandit execution failed: {exc}")

    output = (result.stdout or "").strip()
    if not output:
        stderr_preview = (result.stderr or "").strip()
        if "No module named bandit" in stderr_preview:
            skipped = _make_skipped_result("Bandit module is not installed in the active Python environment.")
            skipped["engine"] = "bandit"
            return skipped
        if stderr_preview:
            return _make_error_result(f"Bandit produced no JSON output. stderr: {stderr_preview[:200]}")
        return {"status": "ok", "issues": 0, "details": [], "mitigations": [], "engine": "bandit"}

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        return _make_error_result(f"Failed to parse Bandit JSON: {exc}")

    details = []
    mitigations = []
    for finding in parsed.get("results", []):
        severity = finding.get("issue_severity", "LOW").upper()
        confidence = finding.get("issue_confidence", "LOW").upper()
        if not _severity_confidence_passes(severity, confidence, min_severity, min_confidence):
            continue

        issue_id = finding.get("test_id", "UNKNOWN")
        details.append(
            {
                "type": issue_id,
                "severity": severity,
                "confidence": confidence,
                "line": finding.get("line_number"),
                "description": finding.get("issue_text"),
                "more_info": finding.get("more_info", ""),
            }
        )
        mitigations.append(
            {
                "issue_id": issue_id,
                "suggested_fix": MITIGATIONS.get(
                    issue_id,
                    f"Review guidance for {issue_id} and apply secure coding practices.",
                ),
            }
        )

    return {
        "status": "ok",
        "issues": len(details),
        "details": details,
        "mitigations": mitigations,
        "engine": "bandit",
    }


def _run_shellcheck(
    file_path: str,
    min_severity: str,
    min_confidence: str,
    timeout: int,
) -> dict:
    shellcheck_path = shutil.which("shellcheck")
    if not shellcheck_path:
        return _make_skipped_result("ShellCheck is not installed.")

    try:
        result = subprocess.run(
            [shellcheck_path, "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _make_error_result(f"ShellCheck timed out after {timeout}s")
    except Exception as exc:
        return _make_error_result(f"ShellCheck execution failed: {exc}")

    output = (result.stdout or "").strip()
    if not output:
        return {
            "status": "ok",
            "issues": 0,
            "details": [],
            "mitigations": [],
            "engine": "shellcheck",
        }

    try:
        findings = json.loads(output)
    except json.JSONDecodeError as exc:
        return _make_error_result(f"Failed to parse ShellCheck JSON: {exc}")

    details = []
    mitigations = []
    for finding in findings:
        code = str(finding.get("code", ""))
        issue_id = f"SHELLCHECK_SC{code}" if code else "SHELLCHECK_UNKNOWN"
        severity = "MEDIUM"
        confidence = "MEDIUM"
        if not _severity_confidence_passes(severity, confidence, min_severity, min_confidence):
            continue
        details.append(
            {
                "type": issue_id,
                "severity": severity,
                "confidence": confidence,
                "line": finding.get("line"),
                "description": finding.get("message", "ShellCheck finding"),
                "more_info": finding.get("level", "style"),
            }
        )
        mitigations.append(
            {
                "issue_id": issue_id,
                "suggested_fix": MITIGATIONS.get(
                    issue_id,
                    "Apply ShellCheck recommendation and enforce strict shell safety patterns.",
                ),
            }
        )

    return {
        "status": "ok",
        "issues": len(details),
        "details": details,
        "mitigations": mitigations,
        "engine": "shellcheck",
    }


def _run_regex_security_rules(
    file_path: str,
    rules: list[tuple[str, str, str]],
    min_severity: str,
    min_confidence: str,
    engine_name: str,
) -> dict:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return _make_error_result(f"File does not exist: {file_path}")

    source = path.read_text(encoding="utf-8", errors="ignore")
    lines = source.splitlines()

    details = []
    mitigations = []
    for issue_id, severity, pattern in rules:
        if not _severity_confidence_passes(severity, "MEDIUM", min_severity, min_confidence):
            continue
        regex = re.compile(pattern)
        for idx, line in enumerate(lines, start=1):
            if regex.search(line):
                details.append(
                    {
                        "type": issue_id,
                        "severity": severity,
                        "confidence": "MEDIUM",
                        "line": idx,
                        "description": f"Potential insecure pattern matched: {issue_id}",
                        "more_info": line.strip()[:240],
                    }
                )
                mitigations.append(
                    {
                        "issue_id": issue_id,
                        "suggested_fix": MITIGATIONS.get(issue_id, "Refactor to a safer language construct."),
                    }
                )

    return {
        "status": "ok",
        "issues": len(details),
        "details": details,
        "mitigations": mitigations,
        "engine": engine_name,
    }


def _run_semgrep(
    file_path: str,
    min_severity: str,
    min_confidence: str,
    timeout: int,
) -> dict:
    semgrep_path = shutil.which("semgrep")
    if not semgrep_path:
        return _make_skipped_result("Semgrep is not installed.")

    try:
        result = subprocess.run(
            [
                semgrep_path,
                "--quiet",
                "--json",
                "--config",
                "p/security-audit",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _make_error_result(f"Semgrep timed out after {timeout}s")
    except Exception as exc:
        return _make_error_result(f"Semgrep execution failed: {exc}")

    output = (result.stdout or "").strip()
    if not output:
        stderr_preview = (result.stderr or "").strip()
        if stderr_preview:
            return _make_error_result(f"Semgrep produced no JSON output. stderr: {stderr_preview[:200]}")
        return {"status": "ok", "issues": 0, "details": [], "mitigations": [], "engine": "semgrep"}

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        return _make_error_result(f"Failed to parse Semgrep JSON: {exc}")

    details = []
    mitigations = []
    for finding in parsed.get("results", []):
        extra = finding.get("extra", {})
        issue_id = finding.get("check_id", "SEMGREP_UNKNOWN")
        severity = str(extra.get("severity", "MEDIUM")).upper()
        confidence = "MEDIUM"
        if not _severity_confidence_passes(severity, confidence, min_severity, min_confidence):
            continue
        details.append(
            {
                "type": issue_id,
                "severity": severity,
                "confidence": confidence,
                "line": (finding.get("start") or {}).get("line"),
                "description": extra.get("message", "Semgrep finding"),
                "more_info": extra.get("metadata", {}).get("shortlink", ""),
            }
        )
        mitigations.append(
            {
                "issue_id": issue_id,
                "suggested_fix": "Apply Semgrep recommendation and refactor toward secure APIs and validated inputs.",
            }
        )

    return {
        "status": "ok",
        "issues": len(details),
        "details": details,
        "mitigations": mitigations,
        "engine": "semgrep",
    }


def get_security_analysis(
    language: str,
    file_path: str,
    min_severity: str = "LOW",
    min_confidence: str = "LOW",
    timeout: int = 60,
) -> dict:
    lang = _normalized_language(language)

    if lang == "python":
        bandit_res = _run_bandit(
            file_path=file_path,
            min_severity=min_severity,
            min_confidence=min_confidence,
            timeout=timeout,
        )
        if bandit_res["status"] in {"ok", "error"}:
            return bandit_res

        return _run_regex_security_rules(
            file_path=file_path,
            rules=PYTHON_RULES,
            min_severity=min_severity,
            min_confidence=min_confidence,
            engine_name="regex-python-fallback",
        )

    if lang == "bash":
        shellcheck_res = _run_shellcheck(
            file_path=file_path,
            min_severity=min_severity,
            min_confidence=min_confidence,
            timeout=timeout,
        )
        if shellcheck_res["status"] in {"ok", "error"}:
            return shellcheck_res

        regex_res = _run_regex_security_rules(
            file_path=file_path,
            rules=[
                ("SHELLCHECK_SC2086", "MEDIUM", r"\$[A-Za-z_][A-Za-z0-9_]*"),
                ("SHELLCHECK_SC2046", "MEDIUM", r"\$\([^)]+\)"),
                ("SHELLCHECK_SC2164", "MEDIUM", r"\bcd\s+[^;&|]+$"),
            ],
            min_severity=min_severity,
            min_confidence=min_confidence,
            engine_name="regex-shell-fallback",
        )
        if regex_res["issues"] == 0:
            regex_res["status"] = "skipped"
            regex_res["reason"] = "ShellCheck unavailable and fallback found no actionable issues."
        return regex_res

    if lang == "javascript":
        semgrep_res = _run_semgrep(
            file_path=file_path,
            min_severity=min_severity,
            min_confidence=min_confidence,
            timeout=timeout,
        )
        if semgrep_res["status"] in {"ok", "error"}:
            return semgrep_res

        return _run_regex_security_rules(
            file_path=file_path,
            rules=JS_RULES,
            min_severity=min_severity,
            min_confidence=min_confidence,
            engine_name="regex-js-rules",
        )

    if lang == "php":
        semgrep_res = _run_semgrep(
            file_path=file_path,
            min_severity=min_severity,
            min_confidence=min_confidence,
            timeout=timeout,
        )
        if semgrep_res["status"] in {"ok", "error"}:
            return semgrep_res

        return _run_regex_security_rules(
            file_path=file_path,
            rules=PHP_RULES,
            min_severity=min_severity,
            min_confidence=min_confidence,
            engine_name="regex-php-rules",
        )

    logger.warning("Unsupported language '%s' for file: %s", language, file_path)
    return _make_skipped_result(f"Unsupported language: '{language}'")
