from __future__ import annotations

from typing import Any


def _skill_list(profile: dict[str, Any]) -> set[str]:
    skills = profile.get("skills", []) or []
    return {str(item).strip().lower() for item in skills}


def _value_for_requirement(profile: dict[str, Any], requirement: dict[str, Any]) -> Any:
    comparison_type = requirement.get("comparison_type", "manual")
    if comparison_type == "cgpa_min":
        return profile.get("cgpa")
    if comparison_type == "graduation_year_min":
        return profile.get("graduation_year")
    if comparison_type == "skill":
        return profile.get("skills", [])
    if comparison_type == "document":
        return profile.get("documents", {}).get(requirement.get("value", ""))
    if comparison_type == "resume":
        return profile.get("resume_url")
    return profile.get(requirement.get("name", "").lower().replace(" ", "_"))


def evaluate_requirements(profile: dict[str, Any], requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for requirement in requirements:
        required = bool(requirement.get("required", True))
        status_value = str(requirement.get("status", "mandatory")).lower()
        comparison_type = requirement.get("comparison_type", "manual")
        name = requirement.get("name", "Requirement")
        expected_value = requirement.get("expected_value", "Not specified")

        if comparison_type == "cgpa_min":
            profile_value = profile.get("cgpa")
            if profile_value is None:
                result_status = "MISSING_INFORMATION"
                explanation = f"No CGPA is available, so the {name} requirement cannot be assessed."
                recommendation = "Add your current CGPA to evaluate this requirement."
            else:
                try:
                    cgpa = float(profile_value)
                    threshold = float(requirement.get("value", 0))
                    if cgpa >= threshold:
                        result_status = "MATCH"
                        explanation = f"Your CGPA of {cgpa} meets the minimum threshold of {threshold}."
                        recommendation = "No action needed for this criterion."
                    else:
                        result_status = "MISMATCH"
                        explanation = f"Your CGPA of {cgpa} is below the minimum threshold of {threshold}."
                        recommendation = "Consider whether you qualify before investing more effort."
                except (TypeError, ValueError):
                    result_status = "MISSING_INFORMATION"
                    explanation = "The current CGPA is not in a usable numeric format."
                    recommendation = "Update your CGPA in the profile so a valid comparison can be made."

        elif comparison_type == "graduation_year_min":
            profile_value = profile.get("graduation_year")
            threshold = requirement.get("value")
            if profile_value is None:
                result_status = "MISSING_INFORMATION"
                explanation = "Your graduation year is missing, so this requirement cannot be confirmed."
                recommendation = "Add your expected graduation year to evaluate the timeline requirement."
            elif int(profile_value) <= int(threshold):
                result_status = "MATCH"
                explanation = f"Your graduation year of {profile_value} fits the required timeline of {threshold} or later."
                recommendation = "No further action required for this condition."
            else:
                result_status = "MISMATCH"
                explanation = f"Your graduation year of {profile_value} does not satisfy the requirement of {threshold} or later."
                recommendation = "Check whether the opportunity is still relevant to your graduation year."

        elif comparison_type == "skill":
            required_skill = str(requirement.get("value", "")).lower()
            profile_skills = _skill_list(profile)
            profile_value = sorted(profile_skills)
            if required_skill in profile_skills:
                result_status = "MATCH"
                explanation = f"Your profile includes {required_skill.title()}, which matches the requirement."
                recommendation = "Keep your portfolio or project evidence ready to demonstrate this skill."
            else:
                if status_value == "preferred":
                    result_status = "MISSING_INFORMATION"
                    explanation = f"The preferred requirement for {required_skill.title()} is not listed in your profile."
                    recommendation = "Add this skill or a project showing it to strengthen your chances."
                else:
                    result_status = "MISSING_INFORMATION"
                    explanation = f"The required skill {required_skill.title()} is not present in your profile."
                    recommendation = "Add the skill or share a relevant project before applying."

        elif comparison_type == "document":
            doc_name = str(requirement.get("value", "")).lower()
            documents = profile.get("documents", {}) or {}
            has_document = bool(documents.get(doc_name))
            profile_value = documents.get(doc_name)
            if has_document:
                result_status = "MATCH"
                explanation = f"Your profile includes {doc_name.title()} as a ready document."
                recommendation = "Keep this document updated and upload it again if needed."
            else:
                result_status = "MISSING_INFORMATION"
                explanation = f"The required document {doc_name.title()} is not available in your profile yet."
                recommendation = "Upload the document or add a valid link before applying."

        elif comparison_type == "resume":
            resume_url = profile.get("resume_url")
            profile_value = resume_url
            if resume_url:
                result_status = "MATCH"
                explanation = "A resume is available in your profile and ready for review."
                recommendation = "Ensure the resume is recent and reflects current skills."
            else:
                result_status = "MISSING_INFORMATION"
                explanation = "No resume has been uploaded or linked."
                recommendation = "Upload a resume before applying."

        else:
            profile_value = _value_for_requirement(profile, requirement)
            if profile_value in (None, "", [], {}):
                result_status = "MISSING_INFORMATION"
                explanation = f"This requirement is not answered in your profile, so it cannot be evaluated yet."
                recommendation = "Share the missing detail or complete this section in your profile."
            else:
                result_status = "MATCH"
                explanation = f"Your profile currently includes the necessary information for {name}."
                recommendation = "No change needed unless you want to improve competitiveness."

        if required is False and result_status == "MISSING_INFORMATION":
            result_status = "MISSING_INFORMATION"

        if result_status == "MISMATCH" and status_value == "preferred":
            result_status = "MISSING_INFORMATION"
            explanation = f"The preferred criterion is not satisfied, but it does not disqualify you from this opportunity."
            recommendation = "Consider improving this area if you want to strengthen your application."

        results.append(
            {
                "name": name,
                "category": requirement.get("category", "general"),
                "required": required,
                "status": result_status,
                "requirement_level": status_value,
                "expected_value": expected_value,
                "profile_value": profile_value if "profile_value" in locals() else None,
                "evaluation_status": result_status,
                "explanation": explanation,
                "recommended_action": recommendation,
            }
        )

    return results
