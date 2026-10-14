# OPPORTUNITYKIT

OPPORTUNITYKIT is a student-first opportunity discovery and readiness platform. It helps students understand whether they match an internship, scholarship, competition, or job requirement, identify missing information, and prepare a practical next-step plan before applying.

## Architecture

- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: FastAPI with Pydantic validation
- Data layer: SQLAlchemy models with SQLite for the MVP (PostgreSQL-ready design)
- Core logic: deterministic rule-based eligibility engine plus requirement extraction helpers

## Features implemented in this MVP

- Student profile management
- Opportunity discovery dashboard
- Manual addition of opportunities
- Requirement extraction from pasted opportunity text
- Eligibility analysis with MATCH / MISMATCH / MISSING_INFORMATION states
- Missing-information follow-up guidance
- Interpretable requirement explanations and recommended actions
- Opportunity-specific requirement checklists for internships, scholarships, and competitions, including profile-aware marks, income, branch, document, team-size, and deadline checks
- Job and internship filters, including profile requirement-fit filtering
- Application tracking with editable application status
- In-browser resume builder with a live print/PDF preview
- Responsive single-page student experience

The resume builder saves its data in the current browser's local storage; it does not upload resumes to the backend. Use **Print / Save PDF** in the builder to export a PDF.

## Quick start

### Docker Compose

With Docker Engine and the Compose plugin installed, run from the project root:

```bash
docker compose up --build
```

Open the app at <http://localhost:5173>. The frontend proxies API requests to the backend service inside Compose; the API is also exposed at <http://localhost:8001>. Stop the services with `Ctrl+C`, or run `docker compose down`. Opportunity and profile data are currently in-memory in the MVP; the Compose volume at `/data` is ready for database persistence when the SQLAlchemy models are wired into the API.

Set `SECRET_KEY` in the environment before deploying beyond local development.

### Backend

```bash
cd backend
/usr/bin/python3.13 -m pip install --break-system-packages -r requirements.txt
/usr/bin/python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 4173
```

## Environment variables

Copy the example file and adjust it as needed:

```bash
cd backend
cp .env.example .env
```

Example values:

```env
DATABASE_URL=sqlite:///./app.db
APP_NAME=OPPORTUNITYKIT
SECRET_KEY=change-me-in-production
CORS_ORIGINS=http://localhost:5173,http://localhost:4173
```

## API overview

- GET /health
- GET /api/profile
- PUT /api/profile
- GET /api/opportunities
- POST /api/opportunities
- POST /api/opportunities/extract
- POST /api/opportunities/{id}/analyze
- GET /api/checklists?opportunity_id={id} (opportunity-specific checklist; ID optional)
- GET /api/applications
- POST /api/applications
- PATCH /api/applications/{id}
- GET /api/dashboard

## Sample data

The app includes demo profile and opportunity data (including an internship, a job, and a scholarship) in `backend/app/seed.py` to demonstrate the workflow without a live external source.

## Testing and validation

Verified successfully:

- `backend`: 3 eligibility regression tests passed under Python 3.13
- `frontend`: production build succeeded with Vite and TypeScript
- Live API smoke test: `/health` returned `{"status": "ok", "app": "OPPORTUNITYKIT"}` and `/api/opportunities` returned two seeded opportunities

## Limitations and future improvements

- The extraction layer is deterministic and rule-based rather than a production LLM integration.
- The project uses SQLite for the MVP; PostgreSQL can be introduced in a later iteration.
- Authentication, document storage, and real scraping are not fully implemented in the MVP.
- Opportunity verification and stale-link detection need external integrations.

## Recommended next steps

1. Add real authentication and user-specific persistence.
2. Add PostgreSQL migrations and more normalized data models.
3. Introduce optional LLM-based extraction behind a validated schema.
4. Add document upload and secure private storage.
5. Expand the recommendation engine and application reminder system.

## Project status

This repository contains a working MVP of the OPPORTUNITYKIT flow: profile, opportunity discovery, extraction, rule-based eligibility analysis, and an application tracker with a responsive dashboard.
