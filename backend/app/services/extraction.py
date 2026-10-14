from __future__ import annotations

import re
from datetime import datetime
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
    marks_match = re.search(
        r"(?:marks?(?:\s+cut[\s-]?off)?|percentage|cut[\s-]?off)\s*"
        r"(?:of|>=|at least|minimum)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        normalized,
    )
    if marks_match and (not cgpa_match or "mark" in normalized or "percentage" in normalized):
        marks = float(marks_match.group(1))
        requirements.append(
            {
                "name": "Marks cutoff",
                "category": "academics",
                "required": True,
                "status": "mandatory",
                "expected_value": f"Minimum {marks:g}%",
                "comparison_type": "marks_min",
                "value": marks,
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

    study_years = {
        "1st": 1, "first": 1,
        "2nd": 2, "second": 2,
        "3rd": 3, "third": 3,
        "4th": 4, "fourth": 4,
    }
    study_year_match = re.search(
        r"\b(1st|first|2nd|second|3rd|third|4th|fourth)\s+year\s+(?:or|and)\s+(?:above|higher)\b",
        normalized,
    )
    if study_year_match:
        study_year = study_years[study_year_match.group(1)]
        requirements.append(
            {
                "name": "Current study year",
                "category": "eligibility",
                "required": True,
                "status": "mandatory",
                "expected_value": f"{study_year} or later",
                "comparison_type": "current_year_min",
                "value": study_year,
            }
        )

    for skill in ["python", "java", "sql", "machine learning", "react", "node.js", "aws", "c++", "c"]:
        skill_pattern = rf"(?<![a-z0-9+#]){re.escape(skill)}(?![a-z0-9+#])"
        skill_match = re.search(skill_pattern, normalized)
        if skill_match:
            preferred_pattern = (
                rf"(?:{skill_pattern})[^.;,\n]{{0,32}}\bpreferred\b"
                rf"|\bpreferred\b[^.;,\n]{{0,32}}(?:{skill_pattern})"
            )
            preferred = re.search(preferred_pattern, normalized) is not None
            requirements.append(
                {
                    "name": skill.title(),
                    "category": "skills",
                    "required": not preferred,
                    "status": "preferred" if preferred else "mandatory",
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

    if "income certificate" in normalized or "proof of income" in normalized:
        requirements.append(
            {
                "name": "Income certificate",
                "category": "documents",
                "required": True,
                "status": "mandatory",
                "expected_value": "Income certificate required",
                "comparison_type": "document",
                "value": "income",
            }
        )

    if "branch" in normalized or "department" in normalized:
        branch_names = {
            "computer science and engineering": "Computer Science",
            "computer science": "Computer Science",
            "cse": "Computer Science",
            "cs": "Computer Science",
            "electronics and communication engineering": "Electronics",
            "electronics and communication": "Electronics",
            "ece": "Electronics",
            "electrical engineering": "Electrical Engineering",
            "mechanical engineering": "Mechanical Engineering",
            "information technology": "Information Technology",
        }
        branch_pattern = "|".join(
            re.escape(branch)
            for branch in sorted(branch_names, key=len, reverse=True)
        )
        accepted_branches = list(dict.fromkeys(
            branch_names[match.group()]
            for match in re.finditer(rf"\b(?:{branch_pattern})\b", normalized)
        ))
        if accepted_branches:
            requirements.append(
                {
                    "name": "Branch eligibility",
                    "category": "eligibility",
                    "required": True,
                    "status": "mandatory",
                    "expected_value": "Accepted branches: " + ", ".join(accepted_branches),
                    "comparison_type": "branch",
                    "value": accepted_branches,
                }
            )

    if "portfolio" in normalized:
        requirements.append(
            {
                "name": "Portfolio",
                "category": "documents",
                "required": True,
                "status": "mandatory",
                "expected_value": "Project portfolio required",
                "comparison_type": "portfolio",
                "value": "portfolio",
            }
        )

    income_match = re.search(
        r"(?:annual |family )?income\s*(?:limit(?: of)?|cut[\s-]?off|is|should be|must be)?\s*"
        r"(?:below|under|at most|not more than|less than|<=|of)?\s*₹?\s*([\d,.]+)\s*(crore|lakh|lac|k)?",
        normalized,
    )
    if income_match and any(word in normalized for word in ("income limit", "family income", "annual income", "income below", "income under")):
        amount = float(income_match.group(1).replace(",", ""))
        unit = income_match.group(2)
        if unit == "crore":
            amount *= 10_000_000
        elif unit in {"lakh", "lac"}:
            amount *= 100_000
        elif unit == "k":
            amount *= 1_000
        requirements.append(
            {
                "name": "Income limit",
                "category": "financial",
                "required": True,
                "status": "mandatory",
                "expected_value": f"Annual income at most ₹{amount:,.0f}",
                "comparison_type": "income_max",
                "value": amount,
            }
        )

    team_range = re.search(r"team(?: size)?\s*(?:of|:)?\s*(\d+)\s*(?:-|to)\s*(\d+)", normalized)
    if team_range:
        minimum, maximum = int(team_range.group(1)), int(team_range.group(2))
        requirements.append(
            {
                "name": "Team size",
                "category": "team",
                "required": True,
                "status": "mandatory",
                "expected_value": f"{minimum} to {maximum} members",
                "comparison_type": "team_size_range",
                "value": {"min": minimum, "max": maximum},
            }
        )
    else:
        team_size = re.search(r"team(?: size)?\s*(?:of|:)?\s+(\d+)", normalized)
        if team_size:
            size = int(team_size.group(1))
            requirements.append(
                {
                    "name": "Team size",
                    "category": "team",
                    "required": True,
                    "status": "mandatory",
                    "expected_value": f"{size} members",
                    "comparison_type": "team_size",
                    "value": size,
                }
            )

    deadline_match = re.search(
        r"deadline\s*(?:is|:|on|by)?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|[a-z]+\s+\d{1,2},?\s+\d{4})",
        normalized,
    )
    if deadline_match:
        deadline_text = deadline_match.group(1)
        deadline = None
        for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%B %d %Y"):
            try:
                deadline = datetime.strptime(deadline_text, date_format).date().isoformat()
                break
            except ValueError:
                continue
        if deadline:
            requirements.append(
                {
                    "name": "Application deadline",
                    "category": "deadline",
                    "required": False,
                    "status": "informational",
                    "expected_value": deadline,
                    "comparison_type": "deadline",
                    "value": deadline,
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
