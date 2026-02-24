import subprocess
import json
import logging

logger = logging.getLogger(__name__)

# Basic dictionary of known Bandit mappings to English mitigations.
# A full version would include all OWASP Top 10 mappings from Bandit.
MITIGATIONS = {
    "B101": "Do not use assert statements in production code.",
    "B105": "Avoid hardcoded passwords; use environment variables or a secure vault.",
    "B106": "Avoid hardcoded passwords; use environment variables or a secure vault.",
    "B303": "Use a secure hashing algorithm like hashlib.sha256 or bcrypt instead of MD5.",
    "B608": "Use parameterized queries or ORMs to prevent SQL injection.",
    "B605": "Avoid starting a process with a partial executable path.",
    "B311": "Standard pseudo-random generators are not suitable for security/cryptographic purposes."
}

def scan_python_code(file_path: str) -> dict:
    """Scans the generated Python code using Bandit."""
    try:
        result = subprocess.run(
            ['bandit', '-f', 'json', file_path],
            capture_output=True,
            text=True
        )
        
        # Bandit exits with 1 if issues are found, 0 if clean.
        # It may return an error but output valid JSON, so we handle both.
        output = result.stdout
        
        if not output:
            return {"issues": 0, "details": [], "mitigations": []}

        data = json.loads(output)
        findings = data.get("results", [])
        
        details = []
        mitigations = []
        
        for finding in findings:
            issue_id = finding.get('test_id')
            details.append({
                "type": finding.get('test_id'),
                "severity": finding.get('issue_severity'),
                "line": finding.get('line_number'),
                "description": finding.get('issue_text')
            })
            
            mitigations.append({
                "issue_id": issue_id,
                "suggested_fix": MITIGATIONS.get(issue_id, "Review the code and remediate manually.")
            })
            
        return {
            "issues": len(findings),
            "details": details,
            "mitigations": mitigations
        }
    except Exception as e:
        logger.error(f"Error scanning Python code {file_path}: {e}")
        return {"issues": 0, "details": [], "mitigations": []}

def scan_js_code(file_path: str) -> dict:
    """Placeholder for JS npm audit / eslint security scanning"""
    # Requires initializing a package.json and running npm audit
    # For now, returning clean result as mock implementation
    return {"issues": 0, "details": [], "mitigations": []}

def get_security_analysis(language: str, file_path: str) -> dict:
    if language.lower() == "python":
        return scan_python_code(file_path)
    elif language.lower() in ["javascript", "js", "node"]:
        return scan_js_code(file_path)
    # Default clean for unsupported languages 
    return {"issues": 0, "details": [], "mitigations": []}
