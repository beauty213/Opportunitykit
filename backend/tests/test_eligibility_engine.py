from app.services.eligibility import evaluate_requirements
from app.services.extraction import extract_requirements_from_text
from app.seed import SAMPLE_OPPORTUNITIES, SAMPLE_PROFILE


def test_match_for_cgpa_requirement():
    profile = {"cgpa": 8.2, "skills": ["Python", "SQL"], "graduation_year": 2027}
    requirements = [{
        "name": "CGPA",
        "category": "academics",
        "required": True,
        "status": "mandatory",
        "expected_value": "Minimum 7.0",
        "comparison_type": "cgpa_min",
        "value": 7.0,
    }]

    results = evaluate_requirements(profile, requirements)
    assert results[0]["status"] == "MATCH"


def test_mismatch_for_failed_mandatory_requirement():
    profile = {"cgpa": 6.5}
    requirements = [{
        "name": "CGPA",
        "category": "academics",
        "required": True,
        "status": "mandatory",
        "expected_value": "Minimum 7.0",
        "comparison_type": "cgpa_min",
        "value": 7.0,
    }]

    results = evaluate_requirements(profile, requirements)
    assert results[0]["status"] == "MISMATCH"


def test_missing_information_for_unlisted_skill():
    profile = {"skills": ["JavaScript"]}
    requirements = [{
        "name": "Python",
        "category": "skills",
        "required": False,
        "status": "preferred",
        "expected_value": "Python experience",
        "comparison_type": "skill",
        "value": "Python",
    }]

    results = evaluate_requirements(profile, requirements)
    assert results[0]["status"] == "MISSING_INFORMATION"


def test_job_opportunity_is_seeded_and_matches_sample_profile():
    categories = {opportunity["category"].lower() for opportunity in SAMPLE_OPPORTUNITIES}
    assert {"job", "internship"} <= categories

    job = next(opportunity for opportunity in SAMPLE_OPPORTUNITIES if opportunity["category"].lower() == "job")
    results = evaluate_requirements(SAMPLE_PROFILE, job["requirements"])
    assert all(
        result["evaluation_status"] != "MISMATCH"
        for result in results
        if result["required"]
    )


def test_unknown_skill_is_missing_but_a_confirmed_absence_is_a_mismatch():
    requirement = [{
        "name": "Python",
        "category": "skills",
        "required": True,
        "status": "mandatory",
        "comparison_type": "skill",
        "value": "python",
    }]

    assert evaluate_requirements({}, requirement)[0]["evaluation_status"] == "MISSING_INFORMATION"
    assert evaluate_requirements({"skills": ["Java"]}, requirement)[0]["evaluation_status"] == "MISMATCH"


def test_scholarship_and_competition_requirements_compare_known_and_unknown_values():
    scholarship_requirements = [
        {"name": "Marks cutoff", "comparison_type": "marks_min", "value": 80},
        {"name": "Income limit", "comparison_type": "income_max", "value": 500000},
        {"name": "Branch", "comparison_type": "branch", "value": ["Computer Science", "ECE"]},
        {"name": "Income certificate", "comparison_type": "document", "value": "income"},
    ]
    scholarship_results = evaluate_requirements(
        {
            "marks": 75,
            "annual_income": 650000,
            "department": "Mechanical",
            "documents": {},
        },
        scholarship_requirements,
    )
    assert [result["evaluation_status"] for result in scholarship_results] == [
        "MISMATCH",
        "MISMATCH",
        "MISMATCH",
        "MISSING_INFORMATION",
    ]

    competition_requirement = [{
        "name": "Team size",
        "comparison_type": "team_size_range",
        "value": {"min": 2, "max": 4},
    }]
    assert evaluate_requirements({}, competition_requirement)[0]["evaluation_status"] == "MISSING_INFORMATION"
    assert evaluate_requirements({"team_size": 5}, competition_requirement)[0]["evaluation_status"] == "MISMATCH"
    assert evaluate_requirements({"team_size": 3}, competition_requirement)[0]["evaluation_status"] == "MATCH"


def test_informational_deadline_does_not_become_a_mandatory_eligibility_failure():
    from app.main import analyze_opportunity, get_checklists

    analysis = analyze_opportunity(3)
    deadline = next(item for item in analysis["results"] if item["name"] == "Application deadline")
    assert deadline["required"] is False
    assert deadline["evaluation_status"] in {"MATCH", "MISMATCH"}
    assert "Application deadline" not in analysis["summary"]["mandatory_mismatches"]

    competition_checklist = get_checklists(4)
    assert {item["comparison_type"] for item in competition_checklist} >= {
        "current_year_min",
        "team_size_range",
        "portfolio",
        "deadline",
    }


def test_requirement_extraction_handles_marks_income_portfolio_team_and_deadline():
    requirements = extract_requirements_from_text(
        "Scholarship marks cutoff 80%, annual income limit 5 lakh, portfolio required. "
        "Python required, SQL preferred. "
        "Competition team size 2-4, second year or above, CS or ECE branch only. "
        "Deadline: 2026-12-01"
    )
    extracted = {item["comparison_type"] for item in requirements}
    assert {
        "marks_min",
        "income_max",
        "portfolio",
        "team_size_range",
        "current_year_min",
        "branch",
        "deadline",
    } <= extracted
    skills = {item["name"].lower(): item for item in requirements if item["category"] == "skills"}
    assert skills["python"]["required"] is True
    assert skills["sql"]["required"] is False
    assert "c" not in skills
