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

### Deploy the frontend on Vercel

This project has a Vite frontend and a separate FastAPI backend. Deploying the frontend on Vercel does not deploy the API. Deploy the backend first (for example, as a Python web service on Render), then connect the frontend to its public URL.

1. **Revoke any exposed GitHub token.** The value pasted into chat has the format of a GitHub Personal Access Token, but its validity cannot be confirmed here. Treat it as compromised: open [GitHub token settings](https://github.com/settings/tokens), revoke it, and do not paste a replacement into chat, source files, or Vercel. Vercel's GitHub app integration does not require you to enter a PAT.
2. **Check the repository.** `https://github.com/beauty213/Opportunitykit` is the GitHub repository URL. Push the project changes you want to deploy to the repository before continuing.
3. **Deploy the API.** In Render, create a new Web Service and connect the repository. Set the root directory to `backend`, the build command to `pip install -r requirements.txt`, and the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. The `backend/.python-version` file pins the service to Python 3.13.14; keep this version pin so older pinned dependencies install prebuilt wheels instead of trying to compile on Python 3.14. Add these backend environment variables:
   - `APP_NAME`: `OPPORTUNITYKIT`
   - `SECRET_KEY`: a new, randomly generated value stored only in the hosting provider's environment settings
   - `CORS_ORIGINS`: your Vercel production origin, for example `https://your-project.vercel.app`
4. **Import the repository into Vercel.** Choose **Add New → Project**, import `beauty213/Opportunitykit`, and set the **Root Directory** to `frontend`. Vercel should detect Vite; use build command `npm run build` and output directory `dist`.
5. **Set the Vercel API URL.** In the Vercel project's **Settings → Environment Variables**, add `VITE_API_BASE` with the public backend origin from step 3 (for example `https://your-api.onrender.com`, without a trailing slash). Select Production, save, and redeploy so the build includes the variable.
6. **Allow the deployed frontend in backend CORS.** Set `CORS_ORIGINS` on the backend to the exact Vercel production origin (and any custom domain origin you use), then restart/redeploy the API.
7. **Verify the deployment.** Open the Vercel URL, then check `https://your-api.onrender.com/health` returns a healthy response. Test loading opportunities and analyzing an opportunity in the app.

The backend currently keeps profile, opportunity, and application data in process memory; deploying it does not make those records persistent. They can reset when the backend restarts or sleeps. The resume builder stores its data in the user's browser. Add a persistent database and storage before relying on production data retention.

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
