from __future__ import annotations

import re
from datetime import date
from typing import Any


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None and value != [] and value != {}


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(str(value).replace(",", "").replace("₹", "").strip())
    except (TypeError, ValueError):
        return None


def _income_number(value: Any) -> float | None:
    if not isinstance(value, str):
        return _number(value)
    match = re.search(r"[\d,.]+", value.replace(",", ""))
    if not match:
        return None
    amount = _number(match.group())
    if amount is None:
        return None
    normalized = value.lower()
    if "crore" in normalized:
        return amount * 10_000_000
    if "lakh" in normalized or "lac" in normalized:
        return amount * 100_000
    if re.search(r"\d\s*k\b", normalized):
        return amount * 1_000
    return amount


def _year_number(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


def _branch_name(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    aliases = {
        "cs": "computer science",
        "cse": "computer science",
        "computer science engineering": "computer science",
        "computer science and engineering": "computer science",
        "ece": "electronics",
        "electronics and communication engineering": "electronics",
        "ee": "electrical engineering",
        "it": "information technology",
    }
    return aliases.get(normalized, normalized)


def _skill_list(profile: dict[str, Any]) -> set[str]:
    skills = profile.get("skills")
    if not isinstance(skills, (list, tuple, set)):
        return set()
    return {str(item).strip().lower() for item in skills if str(item).strip()}


def _document_result(
    profile: dict[str, Any],
    document_name: str,
) -> tuple[str, Any, str, str]:
    document_label = {
        "income": "Income certificate",
        "transcript": "Academic transcript",
        "resume": "Resume",
        "portfolio": "Portfolio",
    }.get(document_name, document_name.replace("_", " ").title())
    documents = profile.get("documents")
    if not isinstance(documents, dict) or document_name not in documents:
        return (
            "MISSING_INFORMATION",
            None,
            f"Your profile does not say whether the {document_label} is ready.",
            f"Confirm whether you have the {document_label} and mark it ready in your profile.",
        )

    value = documents[document_name]
    if isinstance(value, bool):
        is_ready = value
    else:
        normalized = str(value).strip().lower()
        if normalized in {"", "no", "false", "missing", "not uploaded", "not ready", "needed"}:
            is_ready = False
        else:
            is_ready = True
    if is_ready:
        return (
            "MATCH",
            value,
            f"Your profile shows the {document_label} is ready.",
            "Keep this document current and have it ready to submit.",
        )
    return (
        "MISMATCH",
        value,
        f"You marked the {document_label} as not ready, so it does not meet this requirement yet.",
        f"Prepare the {document_label} before applying.",
    )


def evaluate_requirements(
    profile: dict[str, Any],
    requirements: list[dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    context = context or {}

    for requirement in requirements:
        required = bool(requirement.get("required", True))
        status_value = str(requirement.get("status", "mandatory")).lower()
        comparison_type = requirement.get("comparison_type", "manual")
        name = requirement.get("name", "Requirement")
        expected_value = requirement.get("expected_value", "Not specified")
        value = requirement.get("value")
        profile_value: Any = None

        if comparison_type in {"cgpa_min", "marks_min"}:
            profile_field = "cgpa" if comparison_type == "cgpa_min" else "marks"
            profile_value = profile.get(profile_field)
            threshold = _number(value)
            actual = _number(profile_value)
            label = "CGPA" if comparison_type == "cgpa_min" else "marks"
            if actual is None or threshold is None:
                result_status = "MISSING_INFORMATION"
                explanation = f"Your {label} or its valid minimum is missing, so this requirement cannot be assessed."
                recommendation = f"Add your {label} to your profile to check this cutoff."
            elif actual >= threshold:
                result_status = "MATCH"
                explanation = f"Your {label} of {actual:g} meets the minimum of {threshold:g}."
                recommendation = "No action needed for this criterion."
            else:
                result_status = "MISMATCH"
                explanation = f"Your {label} of {actual:g} is below the minimum of {threshold:g}."
                recommendation = "Check whether you meet the cutoff before applying."

        elif comparison_type == "graduation_year_min":
            profile_value = profile.get("graduation_year")
            actual = _year_number(profile_value)
            threshold = _year_number(value)
            if actual is None or threshold is None:
                result_status = "MISSING_INFORMATION"
                explanation = "Your graduation year or the required year is missing, so eligibility cannot be assessed."
                recommendation = "Add your expected graduation year to your profile."
            elif actual >= threshold:
                result_status = "MATCH"
                explanation = f"Your graduation year of {actual} meets the {threshold} or later requirement."
                recommendation = "No further action needed for this condition."
            else:
                result_status = "MISMATCH"
                explanation = f"Your graduation year of {actual} is earlier than the required {threshold} or later."
                recommendation = "Check whether the opportunity accepts your graduation year."

        elif comparison_type == "current_year_min":
            profile_value = profile.get("current_year")
            actual = _year_number(profile_value)
            threshold = _year_number(value)
            if actual is None or threshold is None:
                result_status = "MISSING_INFORMATION"
                explanation = "Your current study year or the minimum year is missing, so this requirement cannot be assessed."
                recommendation = "Add your current year of study to your profile."
            elif actual >= threshold:
                result_status = "MATCH"
                explanation = f"Your current year ({actual}) meets the minimum study year ({threshold})."
                recommendation = "No further action needed for this condition."
            else:
                result_status = "MISMATCH"
                explanation = f"You are in year {actual}, below the minimum study year of {threshold}."
                recommendation = "Check whether students in your current year may participate."

        elif comparison_type == "skill":
            skill = str(value or name).strip().lower()
            skills = _skill_list(profile)
            profile_value = profile.get("skills")
            if not skills:
                result_status = "MISSING_INFORMATION"
                explanation = f"Your skills list is empty or missing, so {skill.title()} cannot be confirmed."
                recommendation = "Add your skills to your profile or confirm whether you have this skill."
            elif skill in skills:
                result_status = "MATCH"
                explanation = f"Your profile lists {skill.title()}, which meets this skill requirement."
                recommendation = "Keep evidence of this skill ready to share."
            else:
                result_status = "MISMATCH"
                explanation = f"Your listed skills do not include the required skill {skill.title()}."
                recommendation = f"Add {skill.title()} if you have it, or review the requirement before applying."

        elif comparison_type in {"document", "resume"}:
            document_name = "resume" if comparison_type == "resume" else str(value or name).strip().lower()
            if comparison_type == "resume" and _nonempty(profile.get("resume_url")):
                result_status = "MATCH"
                profile_value = profile.get("resume_url")
                explanation = "Your profile has a resume link ready."
                recommendation = "Ensure your resume is up to date before submitting."
            else:
                result_status, profile_value, explanation, recommendation = _document_result(profile, document_name)

        elif comparison_type == "portfolio":
            projects = profile.get("projects")
            documents = profile.get("documents")
            portfolio_document = documents.get("portfolio") if isinstance(documents, dict) else None
            profile_value = portfolio_document or projects or profile.get("github_url")
            if _nonempty(portfolio_document) or _nonempty(profile.get("github_url")) or (isinstance(projects, list) and len(projects) > 0):
                result_status = "MATCH"
                explanation = "Your profile includes portfolio or project evidence."
                recommendation = "Choose your most relevant project to include with your application."
            elif projects is None and (not isinstance(documents, dict) or "portfolio" not in documents) and not _nonempty(profile.get("github_url")):
                result_status = "MISSING_INFORMATION"
                explanation = "Your profile does not say whether you have a portfolio or project work."
                recommendation = "Add a portfolio link or project details to your profile."
            else:
                result_status = "MISMATCH"
                explanation = "Your profile indicates that portfolio or project evidence is not available yet."
                recommendation = "Prepare a portfolio or add relevant project work before applying."

        elif comparison_type == "branch":
            profile_value = profile.get("department")
            allowed_branches = value if isinstance(value, list) else [value]
            if not _nonempty(profile_value) or not any(_nonempty(branch) for branch in allowed_branches):
                result_status = "MISSING_INFORMATION"
                explanation = "Your branch or the accepted branches are not specified, so this requirement cannot be checked."
                recommendation = "Add your branch to your profile or confirm which branches are eligible."
            elif any(_branch_name(profile_value) == _branch_name(branch) for branch in allowed_branches):
                result_status = "MATCH"
                explanation = f"Your branch ({profile_value}) is among the accepted branches."
                recommendation = "No action needed for this criterion."
            else:
                result_status = "MISMATCH"
                explanation = f"Your branch ({profile_value}) is not among the listed accepted branches."
                recommendation = "Confirm with the opportunity provider whether your branch is eligible."

        elif comparison_type == "income_max":
            profile_value = profile.get("annual_income")
            if profile_value is None:
                profile_value = profile.get("income")
            actual_income = _income_number(profile_value)
            maximum = _income_number(value)
            if actual_income is None or maximum is None:
                result_status = "MISSING_INFORMATION"
                explanation = "Your numeric annual income or the income limit is missing, so this requirement cannot be assessed."
                recommendation = "Add your annual family income and confirm the opportunity's income limit."
            elif actual_income <= maximum:
                result_status = "MATCH"
                explanation = f"Your annual income ({actual_income:g}) is within the maximum limit of {maximum:g}."
                recommendation = "Have the required income documents ready."
            else:
                result_status = "MISMATCH"
                explanation = f"Your annual income ({actual_income:g}) is above the maximum limit of {maximum:g}."
                recommendation = "Check whether the opportunity allows any exceptions to this income limit."

        elif comparison_type in {"team_size", "team_size_min", "team_size_max", "team_size_range"}:
            profile_value = profile.get("team_size")
            actual = _number(profile_value)
            if isinstance(value, dict):
                minimum = _number(value.get("min"))
                maximum = _number(value.get("max"))
            elif comparison_type == "team_size":
                minimum = _number(value)
                maximum = _number(value)
            else:
                minimum = _number(value) if comparison_type == "team_size_min" else None
                maximum = _number(value) if comparison_type in {"team_size_max", "team_size_range", "team_size"} else None
            if actual is None or (minimum is None and maximum is None):
                result_status = "MISSING_INFORMATION"
                explanation = "Your planned team size or the allowed team size is missing, so this requirement cannot be assessed."
                recommendation = "Add your team size to your profile or confirm the competition's team-size rules."
            elif (minimum is None or actual >= minimum) and (maximum is None or actual <= maximum):
                result_status = "MATCH"
                explanation = f"Your team size of {actual:g} is within the allowed range."
                recommendation = "No action needed for this criterion."
            else:
                result_status = "MISMATCH"
                explanation = f"Your team size of {actual:g} is outside the allowed range."
                recommendation = "Adjust your team to meet the competition's team-size rules."

        elif comparison_type == "deadline":
            deadline = value or context.get("deadline")
            profile_value = deadline
            try:
                due_date = date.fromisoformat(str(deadline)[:10]) if deadline else None
            except ValueError:
                due_date = None
            if due_date is None:
                result_status = "MISSING_INFORMATION"
                explanation = "No valid application deadline is available for this opportunity."
                recommendation = "Confirm the closing date with the opportunity provider."
            elif due_date >= date.today():
                result_status = "MATCH"
                explanation = f"The listed deadline ({due_date.isoformat()}) has not passed."
                recommendation = "Plan to submit before the deadline."
            else:
                result_status = "MISMATCH"
                explanation = f"The listed deadline ({due_date.isoformat()}) has passed."
                recommendation = "Check whether late applications or a new application round are available."

        else:
            profile_value = profile.get(str(name).lower().replace(" ", "_"))
            result_status = "MISSING_INFORMATION"
            explanation = f"This requirement ({name}) needs a clear comparison and cannot be confirmed automatically."
            recommendation = "Confirm this requirement with the opportunity provider and record the answer in your profile."

        if result_status == "MISMATCH" and status_value == "preferred":
            result_status = "MISSING_INFORMATION"
            explanation = "This preferred criterion is not confirmed; it does not by itself disqualify you."
            recommendation = "Consider improving or documenting this area to strengthen your application."

        results.append(
            {
                "name": name,
                "category": requirement.get("category", "general"),
                "required": required,
                "status": result_status,
                "requirement_level": status_value,
                "expected_value": expected_value,
                "profile_value": profile_value,
                "evaluation_status": result_status,
                "explanation": explanation,
                "recommended_action": recommendation,
            }
        )

    return results
