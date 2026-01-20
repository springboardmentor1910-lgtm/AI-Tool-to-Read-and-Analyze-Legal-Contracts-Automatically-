import re
from typing import List

def normalize_clause(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def is_valid_clause(text: str) -> bool:
    return len(text) > 40

def extract_clause(elements) -> List[str]:
    blocks = [str(el).strip() for el in elements if str(el).strip()]
    full_text = '\n'.join(blocks)

    clause_pattern = r"""
    \n\s*\d+\.\s+ |
    \n\s*\(\w+\)\s+ |
    \n\s*Provided\ that |
    \n\s*Explanation: |
    \n\s*Section\s+\d+ |
    \n\s*Chapter\s+\w+ |
    \n\s*ARTICLE\s+\w+
    """

    raw_clauses = re.split(clause_pattern, full_text, flags = re.I | re.VERBOSE)

    clauses = []
    for c in raw_clauses:
        c = normalize_clause(c)
        if is_valid_clause(c):
            clauses.append(c)

    return clauses

