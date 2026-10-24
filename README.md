# KreatorBuzz
## Create Your Own Buzz

**AI Creator Marketplace & Production Collaboration Atelier**

[![Live App](https://img.shields.io/badge/Live%20App-kreatorbuzz.onrender.com-blue?style=for-the-badge)](https://kreatorbuzz.onrender.com)
[![API Status](https://img.shields.io/badge/API-kreatorbuzz--api.onrender.com-success?style=for-the-badge)](https://kreatorbuzz-api.onrender.com/docs)
[![Database](https://img.shields.io/badge/PostgreSQL-Render%20Cloud-336791?style=for-the-badge&logo=postgresql)](https://render.com)
[![Stack](https://img.shields.io/badge/FastAPI%20%2B%20React-Production-teal?style=for-the-badge)](https://kreatorbuzz.onrender.com)

- **Live Application:** [https://kreatorbuzz.onrender.com](https://kreatorbuzz.onrender.com)
- **Interactive API Docs:** [https://kreatorbuzz-api.onrender.com/docs](https://kreatorbuzz-api.onrender.com/docs)
- **API Base URL:** [https://kreatorbuzz-api.onrender.com/api](https://kreatorbuzz-api.onrender.com/api)

---

## Overview

**KreatorBuzz** is an end-to-end AI creator marketplace and production management atelier connecting high-growth brands and creative recruiters with vetted generative AI directors, designers, and visual artists.

From natural language brief scoping with our AI copilot to deterministic matching, blind aesthetic evaluation, milestone-driven production, automated pre-flight deliverable checks, and real-time project risk rescue, KreatorBuzz replaces fragmented chats and emails with a dedicated, professional collaboration system.

---

## Problem

1. **Unstructured Briefs:** Brands struggle to articulate exact generative AI parameters (aspect ratios, render formats, turnaround times, and usage licenses).
2. **Hallucinated Directories & Unverified Portfolios:** Generic LLMs invent creators and portfolio links that do not exist, wasting recruitment hours.
3. **Subjective Hiring Bias:** Recruiters pick creators based on prestige or superficial metrics rather than pure aesthetic output and technical fit.
4. **Licensing Ambiguity:** AI-generated media often lacks clear commercial, modification, and platform rights, creating legal risk.
5. **Chaotic Delivery & Version Sprawl:** File transfers over cloud drives lack automated specification validation, resulting in broken aspect ratios, missing codecs, and endless unmanaged revisions.
6. **Project Stalls & Abandonment:** When creative milestones encounter delays or communication breakdowns, recruiters have no proactive early warning system or seamless replacement path.

---

## Solution

KreatorBuzz provides an integrated, structured platform designed specifically for the generative AI creative workflow:
- **Conversational Brief Copilot:** Automatically extracts deliverables, budgets, milestone plans, and commercial criteria.
- **100-Point Algorithmic Creator Matching:** Deterministically scores creators against real database records based on toolstack, category, budget headroom, and historical performance.
- **Blind Arena:** An unbiased, anonymized comparison interface where recruiters evaluate work side-by-side without creator names or vanity metrics.
- **Structured Proposal Lifecycle:** Formal proposal state machine transitioning directly into auto-provisioned workspaces upon acceptance.
- **Workspace 2.0:** Encrypted messaging, milestone tracking, deliverable dropzones, and revision tickets.
- **Buzz Check:** Automated pre-flight deliverable auditing validating aspect ratio, resolution, duration, and file specifications.
- **Project Health & Project Rescue:** Autonomous telemetry monitoring milestone velocity and offering one-click plan adjustment or replacement creator handoff.

---

## Key Features

### Creator Matching
- Grounded 100-point multi-factor matching engine.
- Evaluates category alignment (30 pts), toolstack compatibility (25 pts), rate/budget headroom (20 pts), SLA & on-time delivery score (15 pts), and rating confidence (10 pts).
- Ranks verified creators instantly with zero hallucination.

### Blind Arena
- Head-to-head portfolio comparison between two creators.
- Masks creator identities, follower counts, and avatars.
- Recruiters vote on pure aesthetic and technical quality before revealing identities, eliminating hiring bias.

### Trust Signals
- Multi-dimensional trust badges: Identity Verified, Benchmark Portfolio Proven, Commercial Rights Certified, and SLA Score (up to 100%).
- Verified client reviews attached strictly to completed, paid workspaces.

### Licensing
- Deterministic licensing compatibility engine evaluating:
  - Commercial use permissions
  - Usage channels (paid ads, organic social, broadcast, print)
  - Geographic territory (regional, national, worldwide)
  - Term duration (1 to 24+ months)
  - Exclusivity rights and derivative modification permissions
- Instant compatibility checks flag licensing gaps before proposals are accepted.

### Proposal Lifecycle
- Recruiter issues structured proposal with milestones, budget, and deliverable expectations.
- State transitions: `pending` ➔ `accepted` or `declined`.
- On acceptance: Automatically provisions dedicated Workspace, assigns roles, and locks milestone amounts.

### Workspace 2.0
- Real-time milestone tracker (`discovery` ➔ `brief_approved` ➔ `production` ➔ `review` ➔ `completed`).
- Encrypted messaging at rest using Fernet symmetric encryption.
- Direct member communication between recruiter and creator.

### Revisions & Version History
- Formal revision tickets tied to specific milestones or deliverables.
- Structured versioning (`v1`, `v2`, `v3`) with side-by-side asset comparison.
- Clear audit trail of creator notes and client feedback.

### Buzz Check
- Automated pre-flight inspection for uploaded creative deliverables.
- Verifies technical standards: minimum resolution, aspect ratios (16:9, 9:16, 1:1), duration limits, and media containers.
- Generates a 100-point readiness score with actionable warnings before submission to client.

### Project Health
- Real-time autonomous workspace telemetry.
- Evaluates deadline proximity, unaddressed revision count, milestone velocity, and message frequency.
- Categorizes project state: `On Track`, `At Risk`, or `Critical`.

### Project Rescue
- Emergency intervention framework triggered when project health drops or severe delays occur.
- Autonomous options:
  1. **Adjust Plan:** Automatically re-balances remaining milestone timelines and deadlines.
  2. **Continue with Creator:** Logs explicit sponsor continuation with targeted mitigation notes.
  3. **Initiate Replacement:** Automatically discovers top-ranked alternative creators in the same discipline and packages a complete contextual handoff pack with protected remaining budget.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, React Router v7 |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy 2.0, Pydantic v2 |
| **Production Database** | Render PostgreSQL (Singapore region, managed) |
| **Local Database** | SQLite (`backend/maccall.db`) fallback |
| **Authentication** | JWT (JSON Web Tokens) + bcrypt password hashing |
| **Encryption** | Cryptography (Fernet symmetric encryption at rest) |
| **Hosting & Deployment** | Render (Web Service + Static Site + Managed Postgres) |

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                   React 19 Frontend                    │
│      https://kreatorbuzz.onrender.com (Render Static)   │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS / CORS REST
┌──────────────────────────▼─────────────────────────────┐
│                   FastAPI Backend                      │
│      https://kreatorbuzz-api.onrender.com (Web Svc)    │
│                                                        │
│  ├── /api/auth          (JWT + bcrypt authentication)  │
│  ├── /api/creators      (Discover, profiles, taxonomy) │
│  ├── /api/briefs        (Brief Builder, AI Copilot)    │
│  ├── /api/proposals     (Formal proposal lifecycle)    │
│  ├── /api/workspaces    (Milestones, revisions, files) │
│  ├── /api/licensing     (Rights compatibility matrix)  │
│  ├── /api/comparison    (Blind Arena & Trust Signals)  │
│  ├── Buzz Check Engine  (Pre-flight deliverable audit) │
│  └── Project Rescue     (Workspace health & telemetry) │
└──────────────────────────┬─────────────────────────────┘
                           │ Private Network (PostgreSQL)
┌──────────────────────────▼─────────────────────────────┐
│                 Render PostgreSQL 16                   │
│       kreatorbuzz-db (Singapore Cloud Datastore)       │
│                                                        │
│  27 Relational Tables: users, creator_profiles,        │
│  briefs, proposals, workspaces, milestones, files,     │
│  reviews, revision_requests, buzz_checks, rescue_logs  │
└────────────────────────────────────────────────────────┘
```

---

## Security

- **Password Hashing:** Industry-standard bcrypt hashing via passlib.
- **Authentication:** Stateless signed JWT tokens (`HS256`) with configurable expiration.
- **Message Privacy:** Symmetric encryption at rest via `cryptography.fernet`.
- **CORS Configuration:** Explicit origin whitelisting allowing only verified production frontend and development origins.
- **Database Safety:** SQL injection prevention through SQLAlchemy parameterized ORM queries; no raw unsanitized SQL execution.
- **Zero Secrets Committed:** Environment credentials, JWT secrets, and database strings are managed exclusively via Render environment configurations.

---

## Database

The production database is hosted on **Render PostgreSQL 16** (Singapore):
- Fully managed cloud relational datastore.
- Automatic schema creation via SQLAlchemy `Base.metadata.create_all`.
- Idempotent startup migration and seeding (`backend/init_db.py`).
- Automatic fallback to local SQLite for off-grid developer workstations.

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone Repository
```bash
git clone https://github.com/darrylkillsyou-arch/kreatorbuzz.git
cd kreatorbuzz
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```
API will run at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Application will run at `http://localhost:5173`.

---

## Deployment

KreatorBuzz is deployed natively on Render using the Render CLI:

1. **Render PostgreSQL:**
   - Name: `kreatorbuzz-db`
   - Region: Singapore
   - Version: PostgreSQL 16
2. **Backend Web Service:**
   - Name: `kreatorbuzz-api`
   - Runtime: Python (FastAPI + Uvicorn)
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - URL: `https://kreatorbuzz-api.onrender.com`
3. **Frontend Static Site:**
   - Name: `kreatorbuzz`
   - Runtime: Static (React + Vite)
   - Build: `npm install && npm run build`
   - Publish Directory: `dist`
   - URL: `https://kreatorbuzz.onrender.com`
   - SPA Routing: Configured via Render route rewrite `/*` ➔ `/index.html`.

---

## Testing

### Backend Test Suite (Pytest)
Run the full 51-test suite covering authentication, briefs, creator matching, workspaces, Buzz Check, and Project Rescue:
```bash
cd backend
pytest tests/
```
Result: `51 passed in 72s`.

### Frontend TypeScript & Build
Verify type integrity and compile assets:
```bash
cd frontend
npx tsc -b
npm run build
```
Result: Zero TypeScript errors; production bundle built cleanly in `dist/`.

---

## Demo Accounts

The database includes pre-configured active demo accounts with full project histories:

| Role | Email | Password |
|---|---|---|
| **Recruiter / Brand** | `recruiter@codexero.com` | `Demo@123` |
| **Creator** | `creator@codexero.com` | `Demo@123` |
| **Clean Recruiter** | `cleanrecruiter@codexero.com` | `Demo@123` |
| **Clean Creator** | `cleancreator@codexero.com` | `Demo@123` |

---

## Known Limitations

- **Video Processing:** Live video transcoding and waveform rendering are simulated in pre-flight Buzz Check; actual FFmpeg processing on large 4K files requires dedicated asynchronous background workers (e.g. Celery / Redis) for high-scale enterprise production.
- **LLM Rate Limits:** Brief Generation defaults to high-accuracy deterministic fallback templates when third-party Gemini or Ollama API keys are not supplied.

---

**FINAL LIVE URL:** [https://kreatorbuzz.onrender.com](https://kreatorbuzz.onrender.com)  
**FINAL API URL:** [https://kreatorbuzz-api.onrender.com](https://kreatorbuzz-api.onrender.com)  
**STATUS:** READY FOR HACKATHON SUBMISSION
