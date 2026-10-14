from app.services.eligibility import evaluate_requirements
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
