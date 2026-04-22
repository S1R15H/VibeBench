import subprocess
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

MITIGATIONS = {
    "B101": "Do not use assert statements in production code; use explicit conditionals and raise appropriate exceptions.",
    "B102": "Avoid using exec(); it can execute arbitrary code and is a common attack vector.",
    "B103": "Ensure file permissions are set appropriately; avoid overly permissive modes like 0o777.",
    "B104": "Binding to 0.0.0.0 exposes the service on all interfaces; bind to a specific interface in production.",
    "B105": "Avoid hardcoded passwords; use environment variables or a secrets manager.",
    "B106": "Avoid hardcoded passwords in function default arguments; use environment variables or a secrets manager.",
    "B107": "Avoid hardcoded passwords in function arguments; use environment variables or a secrets manager.",
    "B108": "Use a secure, application-specific temp directory rather than /tmp or /var/tmp.",
    "B110": "Avoid bare except/pass blocks that silently swallow exceptions; log or re-raise them.",
    "B112": "Avoid continue in bare except blocks; handle exceptions explicitly.",
    "B201": "Flask debug mode exposes an interactive debugger; never enable it in production.",
    "B301": "Use json or another safe serializer instead of pickle, which can execute arbitrary code on deserialization.",
    "B302": "Use json instead of marshal for serialization; marshal is not secure against malicious data.",
    "B303": "MD5 and SHA1 are cryptographically broken; use hashlib.sha256 or bcrypt for security-sensitive hashing.",
    "B304": "This cipher or mode is considered weak; use AES-GCM or another modern authenticated encryption scheme.",
    "B305": "This cipher mode (e.g. ECB) is insecure; use CBC or GCM with a random IV.",
    "B306": "mktemp() is insecure; use tempfile.mkstemp() or tempfile.NamedTemporaryFile() instead.",
    "B307": "eval() executes arbitrary code; avoid it or use ast.literal_eval() for safe literal parsing.",
    "B308": "mark_safe() bypasses Django's XSS protection; ensure the content is truly safe before using it.",
    "B310": "Validate and sanitize URLs before using urllib to open them to prevent SSRF attacks.",
    "B311": "random is not cryptographically secure; use the secrets module for security-sensitive randomness.",
    "B312": "telnetlib transmits data in plaintext; use paramiko or another SSH library instead.",
    "B313": "Use defusedxml instead of xml.etree to prevent XML injection and entity expansion attacks.",
    "B314": "Use defusedxml instead of xml.etree to prevent XML injection and entity expansion attacks.",
    "B315": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B316": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B317": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B318": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B319": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B320": "Use defusedxml to parse XML and prevent entity expansion (XXE) attacks.",
    "B321": "FTP transmits credentials and data in plaintext; use SFTP or FTPS instead.",
    "B322": "input() in Python 2 evaluates expressions; use raw_input() or migrate to Python 3.",
    "B323": "Unverified SSL context disables certificate validation; always verify certificates in production.",
    "B324": "MD5/SHA1 are weak; use hashlib.sha256 or stronger for any security-sensitive purpose.",
    "B325": "mktemp() is insecure; use tempfile.mkstemp() instead.",
    "B401": "Importing telnetlib; prefer SSH-based libraries like paramiko.",
    "B402": "Importing ftplib; prefer SFTP or FTPS-capable libraries.",
    "B403": "Importing pickle is a security risk if used with untrusted data; consider json or another safe format.",
    "B404": "Importing subprocess; ensure shell=False and validate all inputs to avoid command injection.",
    "B405": "Importing xml.etree; use defusedxml to prevent XXE and injection attacks.",
    "B406": "Importing xml.sax; use defusedxml to prevent XXE and injection attacks.",
    "B407": "Importing xml.expat; use defusedxml to prevent XXE and injection attacks.",
    "B408": "Importing xml.dom; use defusedxml to prevent XXE and injection attacks.",
    "B409": "Importing xml.etree.cElementTree; use defusedxml to prevent XXE and injection attacks.",
    "B410": "Importing lxml; use defusedxml or enable lxml's security features explicitly.",
    "B411": "xmlrpc is vulnerable to DoS attacks via large responses; consider REST APIs with proper rate limiting.",
    "B412": "httpoxy vulnerability in CGI; ensure HTTP_PROXY is not used to set the outbound proxy.",
    "B413": "pycrypto is unmaintained and has known vulnerabilities; use pycryptodome or cryptography instead.",
    "B501": "SSL/TLS certificate verification is disabled; always verify certificates in production.",
    "B502": "SSL v2 and v3 are deprecated and insecure; use TLSv1.2 or higher.",
    "B503": "Using an insecure SSL/TLS protocol version; use TLSv1.2 or higher.",
    "B504": "SSL context does not set a minimum TLS version; explicitly set minimum_version=TLSv1_2.",
    "B505": "Weak RSA/DSA key size; use at least 2048-bit RSA or 256-bit EC keys.",
    "B506": "yaml.load() with an arbitrary loader can execute arbitrary Python; use yaml.safe_load() instead.",
    "B507": "Paramiko host key verification is disabled; always verify host keys to prevent MITM attacks.",
    "B601": "Paramiko exec_command with shell interpolation risks command injection; validate and sanitize inputs.",
    "B602": "subprocess with shell=True is vulnerable to shell injection; use shell=False with a list of arguments.",
    "B603": "subprocess without shell=True; ensure all inputs are validated to prevent argument injection.",
    "B604": "Function call with shell=True detected; prefer shell=False and pass arguments as a list.",
    "B605": "Starting a process with os.system or partial path risks command injection; use subprocess with full paths.",
    "B606": "Starting a process with no arguments detected; verify this is intentional.",
    "B607": "Starting a process with a partial executable path; use the full absolute path to prevent PATH hijacking.",
    "B608": "String-based SQL query construction risks SQL injection; use parameterized queries or an ORM.",
    "B609": "Wildcard injection in Linux commands; avoid shell wildcards with untrusted input.",
    "B610": "Django extra() with user-controlled data risks SQL injection; use ORM filters or RawSQL with params.",
    "B611": "Django RawSQL with user-controlled data risks SQL injection; always pass params separately.",
    "B701": "Jinja2 autoescape is disabled; enable it to prevent XSS vulnerabilities.",
    "B702": "Use of Mako templates without escaping can lead to XSS; enable autoescape or escape manually.",
    "B703": "Django mark_safe() bypasses XSS protection; ensure content is truly safe.",
}


def _make_error_result(reason: str) -> dict:
    """Returns a standardised error result."""
    return {"status": "error", "reason": reason, "issues": 0, "details": [], "mitigations": []}


def _make_skipped_result(reason: str) -> dict:
    """Returns a standardised skipped result."""
    return {"status": "skipped", "reason": reason, "issues": 0, "details": [], "mitigations": []}


def scan_python_code(
    file_path: str,
    min_severity: str = "LOW",
    min_confidence: str = "LOW",
    timeout: int = 60,
) -> dict:
    """
    Scans a Python file for security issues using Bandit.

    Args:
        file_path:      Path to the .py file to scan.
        min_severity:   Minimum Bandit severity to include ('LOW', 'MEDIUM', 'HIGH').
        min_confidence: Minimum Bandit confidence to include ('LOW', 'MEDIUM', 'HIGH').
        timeout:        Seconds before the Bandit subprocess is killed.

    Returns:
        A dict with keys: status, issues, details, mitigations.
        status is one of 'ok', 'error', or 'skipped'.
    """
    # --- input validation ---
    path = Path(file_path)
    if not path.exists():
        logger.error("File does not exist: %s", file_path)
        return _make_error_result(f"File does not exist: {file_path}")
    if not path.is_file():
        logger.error("Path is not a file: %s", file_path)
        return _make_error_result(f"Path is not a file: {file_path}")
    if path.suffix.lower() != ".py":
        logger.error("Expected a .py file, got: %s", file_path)
        return _make_error_result(f"Expected a .py file, got suffix '{path.suffix}'")

    min_sev_rank = SEVERITY_RANK.get(min_severity.upper(), 1)
    min_conf_rank = SEVERITY_RANK.get(min_confidence.upper(), 1)

    # --- run bandit ---
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.error("Bandit timed out after %ds for: %s", timeout, file_path)
        return _make_error_result(f"Bandit timed out after {timeout}s")
    except FileNotFoundError:
        logger.error("Bandit is not installed or not accessible via sys.executable.")
        return _make_error_result("Bandit is not installed; run: pip install bandit")
    except Exception as exc:
        logger.error("Unexpected error running Bandit on %s: %s", file_path, exc)
        return _make_error_result(str(exc))

    # --- parse output ---
    output = result.stdout.strip()
    error_output = result.stderr.strip()

    if not output:
        if error_output:
            logger.error("Bandit stderr for %s: %s", file_path, error_output)
            return _make_error_result(f"Bandit produced no JSON output. stderr: {error_output[:200]}")
        # Empty file or no statements to analyse — treat as clean
        return {"status": "ok", "issues": 0, "details": [], "mitigations": []}

    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Bandit JSON for %s: %s | raw: %.200s", file_path, exc, output)
        return _make_error_result(f"Failed to parse Bandit output: {exc}")

    # --- build results ---
    findings = data.get("results", [])
    details = []
    mitigations = []

    for finding in findings:
        severity = finding.get("issue_severity", "LOW").upper()
        confidence = finding.get("issue_confidence", "LOW").upper()

        if SEVERITY_RANK.get(severity, 0) < min_sev_rank:
            continue
        if SEVERITY_RANK.get(confidence, 0) < min_conf_rank:
            continue

        issue_id = finding.get("test_id", "UNKNOWN")
        details.append({
            "type": issue_id,
            "severity": severity,
            "confidence": confidence,
            "line": finding.get("line_number"),
            "description": finding.get("issue_text"),
            "more_info": finding.get("more_info", ""),
        })
        mitigations.append({
            "issue_id": issue_id,
            "suggested_fix": MITIGATIONS.get(
                issue_id,
                f"No specific guidance available. "
                f"See https://bandit.readthedocs.io/en/latest/plugins/{issue_id.lower()}.html",
            ),
        })

    return {
        "status": "ok",
        "issues": len(details),
        "details": details,
        "mitigations": mitigations,
    }


def scan_js_code(file_path: str) -> dict:
    """
    Placeholder for JavaScript/Node.js security scanning.

    JavaScript scanning is not yet implemented. Returns a 'skipped' result
    so callers can distinguish this from a clean scan.
    """
    logger.warning("JS scanning is not implemented. Skipping: %s", file_path)
    return _make_skipped_result("JavaScript scanning is not yet implemented.")


def get_security_analysis(
    language: str,
    file_path: str,
    min_severity: str = "LOW",
    min_confidence: str = "LOW",
    timeout: int = 60,
) -> dict:
    """
    Dispatches a security scan based on the given language.

    Args:
        language:       Source language ('python', 'javascript', 'js', 'node').
        file_path:      Path to the source file.
        min_severity:   Minimum Bandit severity to report ('LOW', 'MEDIUM', 'HIGH').
        min_confidence: Minimum Bandit confidence to report ('LOW', 'MEDIUM', 'HIGH').
        timeout:        Seconds before the scanner subprocess is killed.

    Returns:
        A dict with keys: status, issues, details, mitigations.
    """
    lang = language.lower().strip()
    if lang == "python":
        return scan_python_code(
            file_path,
            min_severity=min_severity,
            min_confidence=min_confidence,
            timeout=timeout,
        )
    if lang in {"javascript", "js", "node"}:
        return scan_js_code(file_path)

    logger.warning("Unsupported language '%s' for file: %s", language, file_path)
    return _make_skipped_result(f"Unsupported language: '{language}'")