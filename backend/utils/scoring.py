import math

def calculate_correctness_score(verified: bool, compile_status: str) -> tuple[int, int]:
    """
    Returns (score, max_score)
    10/10 if passed verification.
    5/10 if ran but failed verification.
    0/10 if failed compilation.
    """
    max_score = 10
    if verified:
        return (10, max_score)
    if compile_status == "success":
        return (5, max_score)
    return (0, max_score)

def calculate_security_score(issue_count: int, details: list) -> tuple[int, int]:
    """
    Returns (score, max_score)
    Starts at 10 and subtracts based on severity.
    """
    max_score = 10
    penalty = 0
    for issue in details:
        severity = issue.get("severity", "LOW").upper()
        if severity == "HIGH":
            penalty += 5
        elif severity == "MEDIUM":
            penalty += 2
        else:
            penalty += 1
            
    score = max(0, max_score - penalty)
    return (score, max_score)

def calculate_readability_score(complexity: float, comment_density: float) -> tuple[int, int]:
    """
    Returns (score, max_score)
    Complexity of 1.0-2.0 is ideal (10/10).
    Complexity > 20 is poor (0/10).
    Comment density < 0.05 is penalized.
    """
    max_score = 10
    
    # Complexity component (0-7 points)
    # Ideal: 1.0 -> 7 points. Poor: 15+ -> 0 points.
    if complexity <= 1.5:
        comp_score = 7
    else:
        comp_score = max(0, 7 - (complexity - 1.5) * 0.5)
        
    # Comment density component (0-3 points)
    # Ideal: 0.2+ -> 3 points. Poor: 0 -> 0 points.
    if comment_density >= 0.2:
        comm_score = 3
    elif comment_density >= 0.1:
        comm_score = 2
    elif comment_density >= 0.05:
        comm_score = 1
    else:
        comm_score = 0
        
    score = math.floor(comp_score + comm_score)
    return (score, max_score)

def format_score(score: int, max_score: int) -> str:
    return f"{score} / {max_score}"
