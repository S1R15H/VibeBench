import json
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    import lizard
except ImportError:
    lizard = None

logger = logging.getLogger(__name__)

_C_STYLE_COMMENT_LANGS = {
    "javascript",
    "js",
    "typescript",
    "ts",
    "php",
    "java",
    "c",
    "cpp",
    "c++",
    "csharp",
    "c#",
    "go",
    "swift",
    "kotlin",
    "scala",
    "rust",
}
_HASH_COMMENT_LANGS = {
    "python",
    "ruby",
    "rb",
    "bash",
    "sh",
    "shell",
    "r",
    "perl",
}

_LANG_TO_EXT = {
    "python": ".py",
    "javascript": ".js",
    "js": ".js",
    "typescript": ".ts",
    "ts": ".ts",
    "php": ".php",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
    "c++": ".cpp",
    "csharp": ".cs",
    "c#": ".cs",
    "go": ".go",
    "swift": ".swift",
    "kotlin": ".kt",
    "ruby": ".rb",
    "rb": ".rb",
    "rust": ".rs",
    "scala": ".scala",
    "r": ".r",
    "bash": ".sh",
    "shell": ".sh",
    "sh": ".sh",
    "perl": ".pl",
}


def _normalized_language(language: str) -> str:
    lang = language.lower().strip()
    if lang in {"node", "js"}:
        return "javascript"
    if lang in {"sh", "shell"}:
        return "bash"
    return lang


def count_comment_lines(source_code: str, language: str = "python") -> int:
    lines = source_code.splitlines()
    lang = _normalized_language(language)
    count = 0

    if lang in _HASH_COMMENT_LANGS:
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                count += 1
            elif lang == "python" and (stripped.startswith('"""') or stripped.startswith("'''")):
                count += 1
                in_docstring = not in_docstring
            elif in_docstring:
                count += 1
    elif lang in _C_STYLE_COMMENT_LANGS:
        in_block = False
        for line in lines:
            stripped = line.strip()
            if in_block:
                count += 1
                if "*/" in line:
                    in_block = False
            elif stripped.startswith("//"):
                count += 1
            elif stripped.startswith("/*"):
                count += 1
                if "*/" not in stripped[2:]:
                    in_block = True
    else:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                count += 1

    return count


def _line_length_metrics(source_code: str) -> dict:
    lines = source_code.splitlines()
    if not lines:
        return {"max_line_length": 0, "long_line_count": 0}
    return {
        "max_line_length": max(len(line) for line in lines),
        "long_line_count": sum(1 for line in lines if len(line) > 120),
    }


def _fallback_complexity(source_code: str) -> float:
    # Look for branching, loops, and logical operators
    complexity_markers = (
        "if ", "elif ", "else", "for ", "while ", "case ", "catch ", "except ",
        "switch ", "&&", "||", "?", "async ", "await ", "yield "
    )
    hits = sum(source_code.count(marker) for marker in complexity_markers)
    
    # Also count indentation level changes (proxy for depth)
    depth = 0
    lines = source_code.splitlines()
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent > 4:
                depth += (indent // 4)
                
    total_lines = max(len(lines), 1)
    # Base complexity is 1.0 + density of markers + depth weight
    return round(1.0 + (hits * 1.5 / total_lines) + (depth / total_lines), 2)


def _analyze_with_lizard(source_code: str, language: str) -> tuple[float, str]:
    if lizard is None:
        return _fallback_complexity(source_code), "fallback-heuristic"

    lang = _normalized_language(language)
    file_ext = _LANG_TO_EXT.get(lang, f".{lang}")
    fake_filename = f"code{file_ext}"

    analysis = lizard.analyze_file.analyze_source_code(fake_filename, source_code)
    if analysis.function_list:
        avg_cc = sum(fn.cyclomatic_complexity for fn in analysis.function_list) / len(analysis.function_list)
    else:
        avg_cc = 1.0
    return round(avg_cc, 2), "lizard"


def _analyze_with_radon_python(source_code: str) -> tuple[float | None, str | None]:
    radon_path = shutil.which("radon")
    if not radon_path:
        return None, None

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as tmp:
        tmp.write(source_code)
        file_path = tmp.name

    try:
        result = subprocess.run(
            [radon_path, "cc", "-j", file_path],
            capture_output=True,
            text=True,
            timeout=20,
        )
        output = (result.stdout or "").strip()
        if not output:
            return None, None
        data = json.loads(output)
        items = data.get(file_path, [])
        if not items:
            return 1.0, "radon"
        avg_complexity = sum(item.get("complexity", 1.0) for item in items) / len(items)
        return round(float(avg_complexity), 2), "radon"
    except Exception as exc:
        logger.warning("Radon readability analysis failed: %s", exc)
        return None, None
    finally:
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception:
            pass


def analyze_readability(source_code: str, language: str) -> dict:
    try:
        total_lines = len(source_code.splitlines())
        if total_lines == 0:
            return {
                "readability_score": 0.0,
                "comment_density": 0.0,
                "max_line_length": 0,
                "long_line_count": 0,
                "readability_engine": "empty",
            }

        comment_lines = count_comment_lines(source_code, language)
        comment_density = round(comment_lines / total_lines, 3)

        lang = _normalized_language(language)
        readability_score = None
        engine = None

        if lang == "python":
            readability_score, engine = _analyze_with_radon_python(source_code)

        if readability_score is None:
            readability_score, engine = _analyze_with_lizard(source_code, lang)

        line_stats = _line_length_metrics(source_code)

        return {
            "readability_score": float(readability_score),
            "comment_density": comment_density,
            "max_line_length": line_stats["max_line_length"],
            "long_line_count": line_stats["long_line_count"],
            "readability_engine": engine,
        }

    except Exception as exc:
        logger.error("Readability analysis failed: %s", exc)
        return {
            "readability_score": -1.0,
            "comment_density": 0.0,
            "max_line_length": 0,
            "long_line_count": 0,
            "readability_engine": "error",
        }
