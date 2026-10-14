from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    college: str | None = None
    degree: str | None = None
    department: str | None = None
    current_year: str | None = None
    graduation_year: int | None = None
    cgpa: float | str | None = None
    skills: list[str] | None = None
    projects: list[str] | None = None
    resume_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    income: str | None = None
    category: str | None = None
    documents: dict[str, Any] | None = None


class OpportunityCreate(BaseModel):
    title: str
    organization: str
    category: str = "internship"
    description: str
    location: str | None = None
    remote: str | None = None
    deadline: str | None = None
    application_url: str | None = None
    source_url: str | None = None
    requirements: list[dict[str, Any]] = Field(default_factory=list)


class OpportunityText(BaseModel):
    text: str


class ApplicationUpdate(BaseModel):
    opportunity_id: int
    status: str | None = None
    application_date: str | None = None
    notes: str | None = None
    reminder_date: str | None = None
