import radon.complexity as radon_cc
import logging

logger = logging.getLogger(__name__)

def count_comment_lines(source_code: str, language: str = "python") -> int:
    """Simple comment counting for basic metrics."""
    lines = source_code.splitlines()
    count = 0
    if language.lower() == "python":
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                count += 1
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                count += 1
                in_docstring = not in_docstring
            elif in_docstring:
                count += 1
    elif language.lower() in ["javascript", "js", "php"]:
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                count += 1
            elif stripped.startswith("/*"):
                count += 1
                in_block_comment = True
            elif in_block_comment:
                count += 1
                if "*/" in line:
                    in_block_comment = False
    return count

def analyze_readability(source_code: str, language: str) -> dict:
    """
    Returns cyclomatic complexity and comment density.
    Radon is used for Python cyclomatic complexity.
    """
    try:
        total_lines = len(source_code.splitlines())
        if total_lines == 0:
            return {"readability_score": 0.0, "comment_density": 0.0}

        comment_lines = count_comment_lines(source_code, language)
        comment_density = comment_lines / total_lines

        cc_score = 0.0
        if language.lower() == "python":
            results = radon_cc.cc_visit(source_code)
            if results:
                cc_score = sum(r.complexity for r in results) / len(results)
            else:
                cc_score = 1.0 # default CC
        else:
            # We don't have a cyclomatic complexity parser configured for JS/PHP yet
            cc_score = -1.0 

        return {
            "readability_score": round(cc_score, 2),
            "comment_density": round(comment_density, 3)
        }
    except Exception as e:
        logger.error(f"Error performing readability analysis: {e}")
        return {"readability_score": -1.0, "comment_density": 0.0}
