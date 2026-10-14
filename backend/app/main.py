from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, CORS_ORIGINS
from app.schemas import ApplicationUpdate, OpportunityCreate, OpportunityText, ProfileUpdate
from app.seed import SAMPLE_APPLICATIONS, SAMPLE_OPPORTUNITIES, SAMPLE_PROFILE
from app.services.eligibility import evaluate_requirements
from app.services.extraction import extract_requirements_from_text

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROFILE_STATE = {**SAMPLE_PROFILE}
OPPORTUNITIES = [dict(opp) for opp in SAMPLE_OPPORTUNITIES]
APPLICATIONS = [dict(app) for app in SAMPLE_APPLICATIONS]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME}


@app.get("/api/profile")
def get_profile() -> dict[str, Any]:
    return PROFILE_STATE


@app.put("/api/profile")
def update_profile(payload: ProfileUpdate) -> dict[str, Any]:
    data = payload.model_dump(exclude_none=True)
    PROFILE_STATE.update(data)
    return {"status": "updated", "profile": PROFILE_STATE}


@app.get("/api/opportunities")
def get_opportunities() -> list[dict[str, Any]]:
    return OPPORTUNITIES


@app.post("/api/opportunities")
def create_opportunity(payload: OpportunityCreate) -> dict[str, Any]:
    opportunity = payload.model_dump()
    opportunity["id"] = max((item["id"] for item in OPPORTUNITIES), default=0) + 1
    opportunity["verification_status"] = "unverified"
    opportunity["last_checked"] = "Not yet checked"
    OPPORTUNITIES.insert(0, opportunity)
    return {"status": "created", "opportunity": opportunity}


@app.post("/api/opportunities/extract")
def extract_opportunity(payload: OpportunityText) -> dict[str, Any]:
    requirements = extract_requirements_from_text(payload.text)
    return {
        "status": "success",
        "requirements": requirements,
        "warnings": ["AI extraction is deterministic rule-based for this MVP and requires human confirmation."],
    }


@app.post("/api/opportunities/{opportunity_id}/analyze")
def analyze_opportunity(opportunity_id: int) -> dict[str, Any]:
    opportunity = next((item for item in OPPORTUNITIES if item["id"] == opportunity_id), None)
    if not opportunity:
        return {"status": "not_found"}

    requirements = opportunity.get("requirements", [])
    results = evaluate_requirements(PROFILE_STATE, requirements)
    summary = {
        "match": sum(1 for item in results if item["evaluation_status"] == "MATCH"),
        "mismatch": sum(1 for item in results if item["evaluation_status"] == "MISMATCH"),
        "missing": sum(1 for item in results if item["evaluation_status"] == "MISSING_INFORMATION"),
        "mandatory_mismatches": [item["name"] for item in results if item["evaluation_status"] == "MISMATCH" and item["required"]],
    }
    return {
        "opportunity_id": opportunity_id,
        "opportunity": opportunity,
        "results": results,
        "summary": summary,
    }


@app.get("/api/checklists")
def get_checklists() -> list[dict[str, Any]]:
    return OPPORTUNITIES[0].get("requirements", [])


@app.get("/api/applications")
def get_applications() -> list[dict[str, Any]]:
    return APPLICATIONS


@app.post("/api/applications")
def create_application(payload: ApplicationUpdate) -> dict[str, Any]:
    application = payload.model_dump(exclude_none=True)
    application["id"] = max((item["id"] for item in APPLICATIONS), default=0) + 1
    APPLICATIONS.insert(0, application)
    return {"status": "created", "application": application}


@app.patch("/api/applications/{application_id}")
def update_application(application_id: int, payload: ApplicationUpdate) -> dict[str, Any]:
    for index, item in enumerate(APPLICATIONS):
        if item["id"] == application_id:
            APPLICATIONS[index].update(payload.model_dump(exclude_none=True))
            return {"status": "updated", "application": APPLICATIONS[index]}
    return {"status": "not_found"}


@app.get("/api/dashboard")
def get_dashboard() -> dict[str, Any]:
    recommended = [item for item in OPPORTUNITIES if item["category"].lower() in {"internship", "scholarship"}]
    return {
        "recommended_opportunities": recommended,
        "saved_opportunities": OPPORTUNITIES[:2],
        "applications_in_progress": APPLICATIONS,
        "upcoming_deadlines": [item for item in OPPORTUNITIES if item.get("deadline")],
        "profile_completion": 78,
        "missing_documents": ["Income certificate"],
        "preparation_tasks": ["Update resume", "Confirm graduation year", "Upload transcript"],
    }
