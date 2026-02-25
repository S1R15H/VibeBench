import lizard
import logging

logger = logging.getLogger(__name__)

# Languages Lizard supports out of the box (non-exhaustive, used for comment detection routing)
_C_STYLE_COMMENT_LANGS = {
    "javascript", "js", "typescript", "ts", "php", "java", "c", "cpp", "c++",
    "csharp", "c#", "go", "swift", "kotlin", "scala", "rust",
}
_HASH_COMMENT_LANGS = {
    "python", "ruby", "rb", "bash", "sh", "shell", "r", "perl",
}


def count_comment_lines(source_code: str, language: str = "python") -> int:
    """
    Count comment lines for a given source file.
    Handles:
      - Hash-style (#)  for Python, Ruby, Bash, R, Perl, etc.
      - C-style (// and /* */) for JS, PHP, Java, C, C++, Go, Swift, etc.
    """
    lines = source_code.splitlines()
    lang = language.lower()
    count = 0

    if lang in _HASH_COMMENT_LANGS:
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                count += 1
            elif lang == "python" and (
                stripped.startswith('"""') or stripped.startswith("'''")
            ):
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
        # Best-effort: count any line starting with // or #
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                count += 1

    return count


def analyze_readability(source_code: str, language: str) -> dict:
    """
    Returns cyclomatic complexity (via Lizard) and comment density for any
    language Lizard supports (Python, JS, PHP, Java, C/C++, Go, Ruby, etc.).

    Lizard language extension map (passed as file extension):
        python -> .py | javascript -> .js | typescript -> .ts
        php -> .php   | java -> .java     | c -> .c
        cpp -> .cpp   | csharp -> .cs     | go -> .go
        swift -> .swift | kotlin -> .kt   | ruby -> .rb
        rust -> .rs   | scala -> .scala   | r -> .r
    """
    LANG_TO_EXT = {
        "python": ".py",
        "javascript": ".js", "js": ".js",
        "typescript": ".ts", "ts": ".ts",
        "php": ".php",
        "java": ".java",
        "c": ".c",
        "cpp": ".cpp", "c++": ".cpp",
        "csharp": ".cs", "c#": ".cs",
        "go": ".go",
        "swift": ".swift",
        "kotlin": ".kt",
        "ruby": ".rb", "rb": ".rb",
        "rust": ".rs",
        "scala": ".scala",
        "r": ".r",
        "bash": ".sh", "shell": ".sh", "sh": ".sh",
        "perl": ".pl",
    }

    try:
        total_lines = len(source_code.splitlines())
        if total_lines == 0:
            return {"readability_score": 0.0, "comment_density": 0.0}

        comment_lines = count_comment_lines(source_code, language)
        comment_density = comment_lines / total_lines

        lang_key = language.lower()
        file_ext = LANG_TO_EXT.get(lang_key, f".{lang_key}")
        fake_filename = f"code{file_ext}"

        analysis = lizard.analyze_file.analyze_source_code(fake_filename, source_code)

        if analysis.function_list:
            cc_score = sum(fn.cyclomatic_complexity for fn in analysis.function_list) / len(
                analysis.function_list
            )
        else:
            cc_score = 1.0  # Single-block / no functions: minimal complexity

        return {
            "readability_score": round(cc_score, 2),
            "comment_density": round(comment_density, 3),
        }

    except Exception as e:
        logger.error(f"Error performing readability analysis with Lizard: {e}")
        return {"readability_score": -1.0, "comment_density": 0.0}
