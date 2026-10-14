from __future__ import annotations

import re
from typing import Any


def extract_requirements_from_text(text: str) -> list[dict[str, Any]]:
    normalized = text.lower()
    requirements: list[dict[str, Any]] = []

    cgpa_match = re.search(r"cgpa\s*(?:of|>=|at least|minimum)?\s*([0-9]+(?:\.[0-9]+)?)", normalized)
    if cgpa_match:
        requirements.append(
            {
                "name": "CGPA",
                "category": "academics",
                "required": True,
                "status": "mandatory",
                "expected_value": f"Minimum {cgpa_match.group(1)}",
                "comparison_type": "cgpa_min",
                "value": float(cgpa_match.group(1)),
            }
        )

    grad_match = re.search(r"graduation year\s*(?:of|>=|at least|minimum)?\s*(\d{4})", normalized)
    if grad_match:
        requirements.append(
            {
                "name": "Graduation year",
                "category": "academics",
                "required": True,
                "status": "mandatory",
                "expected_value": f"{grad_match.group(1)} or later",
                "comparison_type": "graduation_year_min",
                "value": int(grad_match.group(1)),
            }
        )

    for skill in ["python", "java", "sql", "machine learning", "react", "node.js", "aws", "c++", "c"]:
        if skill in normalized:
            requirements.append(
                {
                    "name": skill.title(),
                    "category": "skills",
                    "required": "preferred" in normalized or skill in {"python", "sql", "react"},
                    "status": "preferred" if "preferred" in normalized else "mandatory",
                    "expected_value": f"{skill.title()} experience",
                    "comparison_type": "skill",
                    "value": skill,
                }
            )

    if "resume" in normalized:
        requirements.append(
            {
                "name": "Resume",
                "category": "documents",
                "required": True,
                "status": "mandatory",
                "expected_value": "Resume uploaded",
                "comparison_type": "resume",
                "value": "resume",
            }
        )

    if "transcript" in normalized or "mark sheet" in normalized:
        requirements.append(
            {
                "name": "Academic transcript",
                "category": "documents",
                "required": True,
                "status": "mandatory",
                "expected_value": "Academic transcript required",
                "comparison_type": "document",
                "value": "transcript",
            }
        )

    if not requirements:
        requirements.append(
            {
                "name": "Manual review",
                "category": "general",
                "required": True,
                "status": "mandatory",
                "expected_value": "Specification should be reviewed manually",
                "comparison_type": "manual",
                "value": "review",
            }
        )

    return requirements
