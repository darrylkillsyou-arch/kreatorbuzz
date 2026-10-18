<div align="center">

# CODE XERO
### AI Content Creator Marketplace & Collaboration Platform

**HacXLerate 2026 Hackathon Submission**

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-codexero--production.up.railway.app-6366f1?style=for-the-badge)](https://codexero-production.up.railway.app)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-7c3aed?style=for-the-badge&logo=railway)](https://railway.app)
[![React](https://img.shields.io/badge/React-18-61dafb?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6?style=for-the-badge&logo=typescript)](https://typescriptlang.org)

</div>

---

## Overview

**CODE XERO** is a full-stack AI-powered marketplace connecting **brands and recruiters** with elite **AI content creators** — spanning AI video production, generative imagery, 3D CGI, fashion campaigns, social media content, animation, graphic design, and AI audio/music.

The platform provides an end-to-end workflow — from discovering creators and generating AI-structured project briefs, to sending proposals, managing collaborative workspaces, tracking deliverables, and building a vibrant creative community.

> **Live Website:** [https://codexero-production.up.railway.app](https://codexero-production.up.railway.app)

---

## Features

### 🔍 Discover Creators
- Browse **50+ seeded AI content creator profiles** across 10+ specialization categories
- Rich profile cards with avatar, category badge, starting rate (₹), rating, and portfolio preview
- Advanced search by name, specialization, or skills
- Category filtering: AI Video, AI Images, 3D & CGI, Fashion, Social Media, Animation, Graphic Design, AI Audio, Product Ads, and more
- Bookmark creators to **Saved Creators** shortlist with cross-session persistence
- One-click **Hire Creator** → launches project proposal flow

### 🤖 AI Project Assistant
- Natural language project description → structured project fields generated via NLP
- Generates: project title, content type, recommended category, deliverables, tools, budget (₹), and timeline
- All generated fields are fully editable before saving
- **Top 3 recommended creators** based on project type and required skills
- Recommendations update dynamically based on category
- **View More Matching Creators** to expand results
- Saved projects persist to SQLite database
- Budget displayed in ₹ (Indian Rupees) throughout

### 🤝 Hiring & Proposals
- Recruiter sends a structured project proposal to a creator with budget (₹) and deadline
- Creator receives proposal under **Project Requests**
- Creator can **Accept** the proposal — triggers workspace creation (idempotent, no duplicates)
- Rejected / pending proposals are tracked with status

### 🏗️ Workspaces
- Accepted proposals create exactly **one private collaboration workspace**
- Workspace visible only to the assigned recruiter and creator — no cross-user leakage
- Workspace contains: milestones, deliverables, messages, and status tracking
- Fresh accounts start with zero unrelated workspaces
- Persistent across refresh, logout, and re-login

### 💬 Community
- Public creative feed shared across all users
- Post types: showcase, tips, behind-the-scenes, work-in-progress, job posting
- **Like / Unlike** with real-time count updates (persists across sessions)
- **Comments** — visible to all users, persist across accounts
- Seeded showcase posts display realistic engagement (1.2K–12.4K likes, 40–2K comments)
- Counts formatted in compact social-media style: `1.2K`, `4.7K`, `12.4K`
- Tool/tag badges on posts
- Post type filtering
- Cross-account post visibility

### 📌 Saved Creators
- Bookmark creator profiles from Discover or profile pages
- Saved Creators panel shows: avatar, category, rating, ₹ starting price, View Profile, Hire Creator, Remove
- "No saved creators yet" empty state with Discover CTA
- Persists after refresh / logout / login
- Separate shortlist per user account

### 🏆 Leaderboard
- Top creator rankings by category
- SLA scores, on-time percentage, review counts
- Luxury AI Creator Director rankings

### 🔔 Notifications
- In-app notification system for proposal events, acceptance, workspace updates

### 🌗 Light / Dark Mode
- Full Light and Dark Mode support across all pages
- Mode preference preserved across sessions

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Database** | SQLite (local) / Persistent Volume (Railway) |
| **ORM** | SQLAlchemy 2.x |
| **Auth** | JWT (python-jose), bcrypt password hashing |
| **AI/NLP** | Google Gemini API (`google-genai`) — optional |
| **Deployment** | Railway (Docker, single-service) |
| **Container** | Docker multi-stage (Node 20 + Python 3.12-slim) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│              React + TypeScript + TailwindCSS (Vite)            │
│                                                                 │
│  Discover │ AI Assistant │ Community │ Workspaces │ Saved       │
└─────────────────────────┬───────────────────────────────────────┘
                          │  HTTPS + /api/* requests
┌─────────────────────────▼───────────────────────────────────────┐
│                  FastAPI (Python 3.12, Uvicorn)                 │
│                                                                 │
│  /api/auth       JWT authentication                             │
│  /api/creators   Creator profiles & search                      │
│  /api/community  Posts, likes, comments                         │
│  /api/proposals  Hire requests, accept/reject                   │
│  /api/workspaces Collaboration spaces                           │
│  /api/shortlist  Saved creators                                 │
│  /api/briefs     AI project briefs                              │
│  /api/search     Full-text search                               │
│                                                                 │
│  Serves React SPA at / for all non-API routes                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│          SQLite Database (maccall.db)                           │
│   Persistent volume mount at /data on Railway                   │
│   50+ creators, demo users, community posts, workspaces         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Local Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

---

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend (from backend/ directory)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend API will be available at: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

---

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server (proxies /api to localhost:8000)
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

### Quick Start (Windows — both services at once)

```powershell
# From the project root
.\start-dev.ps1
```

Or using the batch file:
```cmd
start-dev.bat
```

---

## Database & Demo Seeding

The project includes a pre-seeded SQLite database (`backend/maccall.db`) containing:

- **100+ demo user accounts** (brand users, creators across all categories)
- **50+ creator profiles** with detailed portfolios, rates, and skills
- **Community posts** with realistic engagement counts
- **Sample projects, proposals, and workspaces** for testing all workflows

> ⚠️ The included `maccall.db` contains **demo data only** — no real user PII.

To rebuild the database from scratch (advanced):

```bash
cd backend
python -m app.seed
```

---

## Demo Accounts

Use these verified accounts to explore the full platform:

| Role | Email | Password |
|---|---|---|
| **Demo Recruiter** | `recruiter@codexero.com` | `Demo@123` |
| **Demo Content Creator** | `creator@codexero.com` | `Demo@123` |

> To test the **complete hiring flow**: log in as Demo Recruiter (`recruiter@codexero.com` / `Demo@123`) → Discover → Hire Creator (`creator@codexero.com`) → switch to Demo Content Creator account (`creator@codexero.com` / `Demo@123`) → accept proposal → verify workspace appears for both accounts.

---

## AI Project Assistant

The AI Project Assistant generates structured project briefs from free-form descriptions:

1. Enter a project description (e.g., "Luxury perfume campaign for social media")
2. Click **Generate with AI**
3. The system generates:
   - Project title
   - Content type
   - Recommended category
   - Deliverables list
   - Required tools
   - Budget estimate (₹)
   - Timeline
4. Edit any field
5. Click **Save Project** — persists to database
6. **Top 3 Creator Recommendations** appear based on project type

> ℹ️ If `GEMINI_API_KEY` is not configured, the assistant uses a high-quality NLP-based fallback. No fake "AI" claims are made.

---

## Creator Recommendation Algorithm

Creators are matched to projects based on:
- **Category alignment** — primary specialization match
- **Skills overlap** — tools and techniques required
- **Rating** — higher-rated creators ranked first
- **Availability** — only available creators shown
- **Budget** — starting rate compatibility

---

## Hiring & Workspace Workflow

```
Recruiter → Discover Creators → Click "Hire Creator"
         → Fill: Project Title, Requirement, Budget (₹), Deadline
         → Submit → Proposal created with status: pending

Creator  → Project Requests → View proposal details
         → Click "Accept" → Workspace created (idempotent)
         
Both     → Navigate to Workspaces → Private collaboration space
         → Track milestones, deliverables, messages
```

---

## Testing

### Run Backend Tests

```bash
cd backend

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pytest tests/ -v
```

### Run E2E Verification (against local server)

```bash
# Start both backend and frontend first, then:
python backend/tests/verify_e2e_flow.py
```

---

## Deployment

The project is deployed as a **single Docker container** on Railway:

- **Dockerfile** — multi-stage build: Node 20 (React build) + Python 3.12-slim (FastAPI runner)
- FastAPI serves both the API (`/api/*`) and the React SPA (all other routes)
- SQLite database is stored on a **persistent Railway volume** at `/data/maccall.db`
- The seeded database is automatically copied to the volume on first deploy and **never overwritten**

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up --detach
```

### Environment Variables (Railway)

| Variable | Description |
|---|---|
| `DATABASE_URL` | `sqlite:////data/maccall.db` |
| `GEMINI_API_KEY` | Optional — Gemini AI integration |
| `SECRET_KEY` | JWT signing secret |
| `PORT` | Set automatically by Railway |

---

## Project Structure

```
CODE-XERO/
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/                # Route-level page components
│   │   ├── lib/
│   │   │   ├── api.ts            # Typed API client
│   │   │   ├── mockData.ts       # Demo/fallback data
│   │   │   └── creatorImages.ts  # Avatar & portfolio image mapping
│   │   ├── types/                # TypeScript interfaces
│   │   └── App.tsx               # Root app & routing
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── main.py               # App entry point, SPA serving
│   │   ├── config.py             # Settings (Pydantic BaseSettings)
│   │   ├── database.py           # SQLAlchemy engine & session
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routes/               # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── creators.py
│   │   │   ├── community.py
│   │   │   ├── proposals.py
│   │   │   ├── workspaces.py
│   │   │   ├── shortlist.py
│   │   │   ├── briefs.py
│   │   │   └── ...
│   │   ├── services/             # Business logic & encryption
│   │   ├── dependencies.py       # Auth & JWT helpers
│   │   └── seed.py               # Database seeding script
│   ├── tests/                    # Pytest test suite
│   ├── maccall.db                # Pre-seeded demo SQLite database
│   └── requirements.txt
│
├── Dockerfile                    # Multi-stage production build
├── railway.json                  # Railway deployment config
├── .dockerignore
├── .gitignore
├── start-dev.ps1                 # Windows dev launcher (PowerShell)
├── start-dev.bat                 # Windows dev launcher (CMD)
└── README.md
```

---

## Live Deployment

| Item | Detail |
|---|---|
| **Live URL** | [https://codexero-production.up.railway.app](https://codexero-production.up.railway.app) |
| **Platform** | Railway |
| **Region** | US East (IAD) |
| **Database** | SQLite on persistent volume |
| **Uptime** | Continuous (no sleep on free tier via Railway Hobby) |

---

## HacXLerate 2026

Built for **HacXLerate 2026** — a platform demonstrating:

- 🤖 **AI-assisted creative workflow** — project brief generation and creator matching
- 🏗️ **Full-stack architecture** — React + FastAPI + SQLite deployed as a single container
- 🎨 **Creator economy tooling** — real hiring flows, workspaces, community
- 🌐 **Production-ready deployment** — live, publicly accessible HTTPS URL
- 💡 **Indian market focus** — ₹ pricing, Indian creator profiles, local market context

---

## Contributing

This project was built as a hackathon submission. For questions or feedback, open an issue on the repository.

---

<div align="center">

**Built with ❤️ for HacXLerate 2026**

[Live Demo](https://codexero-production.up.railway.app) · [API Docs](https://codexero-production.up.railway.app/docs)

</div>
