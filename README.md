<div align="center">

# CODE XERO
### AI Content Creator Marketplace & Production Collaboration Atelier

**HacXLerate 2026 Submission**

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-codexero--production.up.railway.app-6366f1?style=for-the-badge)](https://codexero-production.up.railway.app)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-7c3aed?style=for-the-badge&logo=railway)](https://railway.app)
[![React](https://img.shields.io/badge/React-19.2-61dafb?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178c6?style=for-the-badge&logo=typescript)](https://typescriptlang.org)

> **Live Website:** [https://codexero-production.up.railway.app](https://codexero-production.up.railway.app)

</div>

> **One-Line Pitch:** CODE XERO is an end-to-end creative commissioning platform that bridges brands and recruiters with verified generative AI creators through an intelligent AI project copilot, deterministic matching, and private milestone-driven production workspaces.

---

## 📌 What is CODE XERO?

**CODE XERO** is a full-stack web platform built for commissioning, managing, and delivering generative AI creative work. The platform covers 9 specialized AI creative disciplines:
- **AI Video & Synthetic Cinema** (Runway Gen-3, Kling AI, Sora, Luma Dream Machine)
- **AI Images & Generative Stills** (Midjourney v6, Flux.1 Pro, ComfyUI)
- **3D & CGI** (Blender, Unreal Engine 5, Cinema 4D, Spatial Lookdev)
- **Product Advertising & Commercials**
- **Fashion & Digital Runway Lookbooks**
- **Social Media Content & Viral Motion Reels**
- **Animation & Motion Graphics**
- **Branding & Visual Identity**
- **Audio & Voice Synthesis** (ElevenLabs, Suno, Spatial Audio Stems)

Unlike traditional freelance directories that only display portfolio links and leave communication to chaotic emails or DMs, CODE XERO manages the **entire lifecycle of a creative commission**: from conversational brief scoping with **Xero AI**, to grounded creator matching, formal hiring proposals, automated workspace provisioning, versioned deliverable approvals, revision management, and verified client reviews that feed a dynamic monthly leaderboard.

---

## 🎯 Problem Statement

1. **Vague, Underspecified Briefs:** Brands frequently struggle to articulate technical generative AI requirements (e.g. aspect ratios, latent seed provenance, style frames, render passes, turnaround times, and compute costs).
2. **Hallucinated or Unverified Talent:** Generic LLMs and directory bots invent fake creators, cite non-existent portfolios, or recommend creators who do not match the required toolstacks or budget baselines.
3. **Disjointed Collaboration & Version Confusion:** Creative commissioning typically fractures across DMs, Google Drive folders, and unversioned file uploads, leading to lost revisions, missed deadlines, and payment friction.
4. **Unverifiable Reviews:** On traditional platforms, anyone can submit arbitrary 5-star ratings without having executed a verified project, eroding trust for high-value brand commissions.

---

## 💡 Our Solution

CODE XERO provides a structured, trust-first platform with five connected pillars:
1. **Xero AI Copilot:** A conversational assistant that transforms natural language requests into structured project blueprints with deliverables, INR budgets, milestones, and scope warnings.
2. **Grounded 100-Point Algorithmic Matching:** Evaluates actual database records—not hallucinated LLM suggestions—scoring creators across category, toolstack, aesthetic style, budget headroom, and SLA.
3. **Structured Hiring Proposals:** Formal proposal state machine (`pending` ➔ `accepted` / `declined`) eliminating informal agreements.
4. **Private Collaboration Workspaces:** Automatically provisioned upon proposal acceptance, offering milestone trackers, deliverable upload dropzones with automated versioning (`v1`, `v2`), revision tickets, and encrypted chat.
5. **Closed-Loop Verified Reviews & Dynamic Leaderboard:** Reviews can only be submitted after all milestones are completed and released, feeding a dynamic monthly leaderboard that ranks creators based on real project history.

---

## 👥 Main User Roles

- **Brand / Recruiter (`brand`):** Discovers creators across categories, saves shortlists, uses Xero AI to draft and refine project briefs, sends formal proposals with INR budgets and deadlines, tracks active workspaces, reviews deliverable files, requests revisions, approves milestones, and submits verified reviews upon completion.
- **Creator (`creator`):** Showcases specialized AI toolstacks and portfolio items, receives incoming hiring proposals in their Project Requests dashboard, accepts or declines commissions, collaborates inside private workspaces, uploads versioned deliverables, addresses revision requests, and climbs the monthly leaderboard.
- **Administrator (`admin`):** Oversees platform health, directory curation, and global moderation.

---

## 🔄 Complete User Workflow

```
Recruiter / Brand
       │
       ▼
[ Discover Creators ] ────────── OR ──────────▶ [ Xero AI Copilot ]
       │                                                │
       ▼                                                ▼
Filter Category, Tools & Budget                Interactive Multi-Turn Prompt
       │                                                │
       ▼                                                ▼
Save to Shortlist (DB)                         Structured Blueprint Generated
       │                                       (Deliverables, Milestones, Budget, Scope Warning)
       │                                                │
       └───────────────────────┬────────────────────────┘
                               │
                               ▼
                  [ Send Hiring Proposal ]
                  (Targeted to specific creator with INR budget & deadline)
                               │
                               ▼
                  [ Creator: Project Requests ]
                  (Creator reviews terms: Accept or Decline)
                               │
                     ┌─────────┴─────────┐
                  Declined            Accepted
                     │                   │
                  Notified               ▼
                               [ Workspace Provisioned ]
                               (Private to Brand + Creator)
                                         │
                                         ▼
                               [ Production Pipeline ]
                               ├── Milestone Lifecycle (Pending ➔ Approved ➔ Released)
                               ├── Deliverable Uploads (v1 ➔ v2 version tracking)
                               ├── Revision Requests (Open ➔ Resolved)
                               └── Workspace Chat (Encrypted at rest via Fernet)
                                         │
                                         ▼
                               [ All Milestones Released ]
                                         │
                                         ▼
                               [ Project Completed ]
                                         │
                                         ▼
                               [ Verified Review Submitted ]
                               (1-5 Stars + Feedback linked to Workspace)
                                         │
                                         ▼
                               [ Dynamic Monthly Leaderboard ]
                               (Rankings, Category Champions & Awards update)
```

---

## 🌟 All Implemented Features

### 1. Creator Discovery
- Browse categorized creator profiles across 9 core disciplines.
- Profile cards displaying avatars, specialized disciplines, starting rates in INR (₹), SLA reliability scores, verified badges, and portfolio previews.
- Free-text search engine with tokenization, stopword removal, and synonym expansion (`video`, `fashion`, `3d`, `photo`, `sound`).
- Granular filtering by category, toolstack (e.g. Midjourney v6, Runway Gen-3, ComfyUI), style tags, availability status, and rate range.

### 2. Saved Creators / Shortlist
- One-click bookmarking from Discover cards or Creator Profile pages.
- Recruiter-specific shortlist persisted directly in the relational database.
- Dedicated `/saved-creators` dashboard to manage bookmarks or trigger immediate hiring proposals.

### 3. Xero AI Project Planner
- Multi-turn conversational copilot supporting initial prompt exploration and continuous refinement.
- Natural language intent parsing that structures deliverables, platform formats (9:16 Reels, 16:9 4K Master), duration, and creative aesthetic.
- **Scope & Budget Warning Engine:** Evaluates requested deliverables against verified creator day rates, warning recruiters if scope exceeds their stated budget.
- Automatic budget allocation breakdown (65% Production, 15% Generative AI Compute, 12% Post-Processing, 8% Contingency).
- Category-specific 4-stage milestone generation.

### 4. Brief Generation
- Recruiter can review, customize, and save finalized Xero AI project plans into persistent database `Brief` records.
- Preserves all prompt provenance, target platform requirements, style tags, and budget bounds.

### 5. Grounded Creator Recommendations
- Evaluates live database records using an explainable 100-point deterministic matching algorithm.
- Displays top matching creators with a human-readable recommendation rationale (e.g., *"Recommended because this creator specializes in AI Video, uses Runway Gen-3, and fits your ₹60,000 project budget"*).
- Pagination support allowing recruiters to cycle through additional qualified creators.

### 6. Hiring Proposals
- Formal project proposal creation linking a recruiter to an exact creator.
- Specifies project title, detailed requirements, budget in Indian Rupees (₹), and deadline.
- Strict backend validation preventing recruiters from submitting proposals to themselves or non-existent creators.

### 7. Proposal Accept / Decline Flow
- Creators receive proposals in real-time under their **Project Requests** dashboard.
- Immediate actions: **Accept** or **Decline**.
- **Idempotency Guarantee:** Accepting a proposal provisions exactly one workspace; repeated clicks will not create duplicate workspaces.
- Automated notification dispatch alerting the recruiter of the creator's decision.

### 8. Automatic Workspace Creation
- Accepting a proposal automatically triggers workspace provisioning.
- Establishes membership access controls restricting entry exclusively to the commission participants.
- Automatically populates the agreed milestone with the proposal budget and posts an encrypted welcome message in the workspace chat.

### 9. Collaborative Workspaces
- Private, distraction-free atelier for each commission.
- Multi-tab interface: Deliverables / Milestones tracker, Encrypted Chat, and Asset Manager.
- Workspace status state machine: `discovery` ➔ `brief_approved` ➔ `production` ➔ `review` ➔ `delivered` ➔ `completed`.

### 10. Milestone Lifecycle Management
- Phased delivery schedule with clear monetary allocations.
- Milestone status progression: `pending` ➔ `approved` ➔ `released` ➔ `completed`.
- Safety enforcement: Projects cannot be closed if milestones remain unreleased.

### 11. Deliverable File Uploads & Automated Versioning
- File upload dropzone supporting drag-and-drop.
- **Automated Version Tracking:** Uploading an asset to a milestone automatically assigns version numbers (`v1`, `v2`), preserving previous iterations for comparison.
- File security checks: Strict extension whitelisting (`jpg`, `jpeg`, `png`, `webp`, `pdf`, `mp4`, `mov`, `zip`), path traversal sanitization, and a 50 MB upload ceiling.

### 12. Revision Requests
- Recruiter can open formal revision tickets linked directly to specific milestones.
- Tracks revision descriptions and statuses (`open`, `resolved`).
- Strict completion guard: The backend rejects project completion if open revision requests remain unresolved.

### 13. Verified Creator Reviews
- Review submission is locked until the project reaches `completed` status with all milestones released.
- Only the recruiter who commissioned the project can submit a review.
- Enforces 1–5 star rating bounds and qualitative feedback.
- Updates the creator profile's composite rating and displays verified reviews on their public profile.

### 14. Community Creative Feed
- Public feed showcasing creator achievements, service offerings, open briefs, and collaboration requests.
- Social interactions: Real-time likes with persistence, threaded comments, and user follow tracking.
- Tag-based filtering to browse posts by AI toolstack or post category.

### 15. Dynamic Monthly Leaderboard
- Performance ranking engine calculating monthly scores directly from database tables (`workspaces`, `reviews`, `milestones`, `posts`).
- Historical month switching (e.g., August 2026, September 2026, October 2026).
- Ranks top creators overall, highlights category champions, displays rank movement indicators, and awards monthly badges.
- Excludes automated test workspaces from altering live rankings.

### 16. Real-Time Notifications
- In-app alert system for proposal events, milestone status updates, revision requests, and new reviews.
- Unread badge indicators and mark-as-read endpoints.

### 17. Authentication & Role-Based Access Control
- Secure registration and login for `brand` and `creator` roles.
- State-managed session restoration via JWT tokens stored in `localStorage`.
- Protected frontend routes and backend dependencies guarding privileged endpoints.

### 18. Light & Dark Theme System
- Integrated theme switcher persisting user preference in `localStorage`.
- Smooth transition utilizing Tailwind CSS variables and DOM data attributes (`data-theme="light"` / `data-theme="dark"`).
- Defaulted to light mode for optimal editorial clarity.

---

## 🏛️ System Architecture

```
User (Browser)
      │
      ▼
React 19 + TypeScript Frontend (Vite SPA)
      │
      ▼  HTTP REST (JSON Payloads & Multipart Form-Data)
FastAPI Application Server (/api)
      │
      ├── Authentication & RBAC Dependencies (JWT + bcrypt)
      ├── Message Encryption at Rest (Fernet)
      ├── Local Deliverables Storage Manager
      │
      ├──▶ AI Subsystem: 3-Tier Project Copilot
      │       ├── Ollama-Compatible Endpoint (JSON Schema)
      │       ├── Google Gemini (gemini-2.5-flash)
      │       └── Local Heuristic Fallback (Regex & Rules)
      │
      ├──▶ Deterministic 100-Point Creator Matcher (Python Engine)
      │
      ▼
SQLAlchemy 2.0 ORM Engine
      │
      ▼
SQL Database (SQLite for Prototype | PostgreSQL Capable)
```

---

## 💻 Technology Stack & Why We Chose It

| Technology | Purpose in CODE XERO | Simple Reason for Choosing |
| :--- | :--- | :--- |
| **Python** | Backend programming language | Rich ecosystem for AI SDKs, data manipulation, cryptography, and modern async web frameworks. |
| **TypeScript / JavaScript** | Frontend programming language | Prevents runtime type errors across complex objects (briefs, plans, creators, proposals, and milestones). |
| **React (v19.2)** | Frontend UI library | Component-driven model allows creating reusable, interactive UI elements (chat streams, modals, file dropzones, tabbed workspaces). |
| **Vite (v8.3)** | Build tool and dev server | Sub-second Hot Module Replacement (HMR) and optimized production bundling. |
| **React Router (v7.18)** | Client-side routing | Enables declarative page navigation with URL parameters (`/creators/:id`, `/workspaces?id=...`). |
| **Tailwind CSS (v3.4)** | UI styling | Rapid utility-first styling with unified CSS variable tokens for seamless light/dark mode transitions. |
| **FastAPI (v0.110+)** | Backend web framework | High performance async framework with native Pydantic validation and automatic OpenAPI Swagger documentation (`/docs`). |
| **REST APIs** | Client-Server communication | Universal, stateless HTTP standard making frontend and backend cleanly decoupled. |
| **Pydantic (v2.0+)** | Data parsing and validation | Strictly validates incoming request bodies, query parameters, and serializes response payloads. |
| **SQLAlchemy (v2.0+)** | Object-Relational Mapper (ORM) | Bridges Python objects with SQL tables, managing transactions and abstracting database engine differences. |
| **SQL** | Relational data standard | Enforces referential integrity through foreign keys across heavily interconnected project entities. |
| **SQLite** | Prototyping database engine | Serverless, zero-configuration SQL engine stored in a single file (`maccall.db`), ideal for rapid hackathon testing and demo portability. |
| **PostgreSQL** | Production database option | Industrial client-server DBMS. CODE XERO's `database.py` already supports PostgreSQL connection pooling for production scale. |
| **JWT (JSON Web Tokens)** | Authentication tokens | Stateless session handling; allows the frontend to authenticate requests via Bearer headers without database lookups for session state. |
| **bcrypt** | Password hashing | Industry-standard slow hashing algorithm with salt generation to securely store user passwords. |
| **Fernet (cryptography)** | Symmetric message encryption | Encrypts workspace messages at rest in the database using AES-128-CBC and HMAC authentication. |
| **Google Gemini** | Cloud AI integration | Powers Xero AI brief planning using `gemini-2.5-flash` with structured JSON output mode. |
| **Ollama Support** | Local/Cloud AI integration | Supports open-weights and cloud inference using Ollama-compatible `/api/chat` endpoints with JSON formatting. |
| **Rule-Based AI Fallback** | Offline NLP engine | Guarantees zero downtime: extracts budget, timeline, and milestones via regex and rules if external AI APIs are offline or unconfigured. |
| **Git / GitHub** | Version control & repository | Tracks code history, coordinates team development, and provides a transparent submission base for judges. |
| **pytest** | Automated test runner | Provides an isolated in-memory test environment (`sqlite:///:memory:`) to verify routes and business logic. |

---

## 🔍 Architecture Deep Dives

### Why SQL?
CODE XERO has heavily interconnected data:
$$\text{Users} \rightarrow \text{Creator Profiles} \rightarrow \text{Proposals} \rightarrow \text{Workspaces} \rightarrow \text{Milestones} \rightarrow \text{Files} \rightarrow \text{Reviews}$$

A project review cannot exist without a completed workspace. A workspace cannot exist without an accepted proposal. Milestone deliverables cannot exist without a parent milestone. 

**SQL** (the relational database standard) enforces foreign key constraints and ACID transactional guarantees. If any step fails during proposal acceptance, the transaction rolls back cleanly without leaving orphaned records.

### Why SQLite for the Hackathon?
**SQLite** is a full SQL database engine that runs embedded within the Python application, storing all tables in a single local file (`maccall.db`). 

It is ideal for a hackathon prototype because:
- It requires **no external database server** to install, configure, or maintain.
- It enables rapid offline development and automated testing using in-memory databases (`sqlite:///:memory:`).
- It allows the entire state, seed data, and schema to be committed and demonstrated seamlessly.

*(Note: SQL is the relational language and model; SQLite is one specific embedded engine implementing SQL.)*

### Why Not MongoDB / NoSQL?
In document databases like MongoDB, data is nested within documents or referenced loosely without database-enforced relational integrity. 

For CODE XERO, NoSQL would cause two major problems:
1. **Data Inconsistency:** Creator profile updates (rates, specializations) would have to be manually synced across duplicated proposals, briefs, and workspaces.
2. **Lack of Referential Constraints:** MongoDB cannot natively prevent an orphaned review from being created on an incomplete project without complex application-level lock code.

### Why FastAPI?
1. **Lightweight & High Performance:** Built on Starlette and Pydantic, FastAPI is one of the fastest Python frameworks available.
2. **Automatic Interactive Documentation:** Automatically exposes Swagger UI at `/docs` and ReDoc at `/redoc`, allowing judges to inspect and test all 11 API routers.
3. **Seamless AI Integration:** Because FastAPI is native Python, integrating the Gemini SDK, Ollama HTTP calls, and regex fallback services happens in the same runtime without microservice overhead.

### Why React?
The CODE XERO interface is highly dynamic: live chat messages, multi-stage AI prompt generation, modal proposal dialogs, dynamic file upload lists, and theme toggling. React's component-based model and virtual DOM state management allow these complex UI surfaces to remain fast, modular, and maintainable.

---

## 🤖 AI Architecture: Resilient 3-Tier Strategy

CODE XERO is **AI-assisted**, not AI-dependent. It uses a **3-tier resilient architecture**:

```
                         Recruiter Prompt
                                │
                                ▼
                       [ AI Provider Router ]
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   [ Ollama API ]        [ Google Gemini ]     [ Local Fallback ]
   Ollama Cloud / Local   gemini-2.5-flash      Regex & Heuristics
   JSON Format            JSON Mode             100% Offline
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                                ▼
                 [ Structured Project Blueprint ]
       ├── Core Category Clamping (1 of 9 official disciplines)
       ├── INR Budget Parsing & Headroom Allocation
       ├── 4-Phase Discipline Milestone Generation
       └── Deliverable Scope vs Baseline Day Rate Warning Engine
                                │
                                ▼
               [ Grounded Database Creator Matcher ]
          (Direct Python evaluation of live SQL records)
                                │
                                ▼
               Grounded Recommendations & Rationale
```

### Deterministic Safety Guarantee
1. **Grounded Creator Matching:** The external LLM is **never** asked to recommend or invent creators. The LLM only structures the project brief. Recommendations are generated exclusively by querying real `CreatorProfile` records from the SQL database and scoring them in Python.
2. **Offline Hackathon Guarantee:** If external AI API keys are unconfigured or conference Wi-Fi is unavailable, `FallbackAIProvider` automatically activates. It uses deterministic regex and NLP heuristics to extract budgets (`₹`, `Rs`, `k`), timelines, categories, and milestones without showing an error to the user.
3. **No Trained Base Model Claims:** CODE XERO does not claim to have trained a proprietary base model from scratch. We combine prompt-engineered foundation models (Gemini / Ollama) with deterministic Python NLP and rule-based fallback safety.

---

## 🎯 Grounded 100-Point Creator Matching Formula

The matching engine (`backend/app/services/matching.py`) evaluates real database profiles using a transparent formula:

$$\text{Total Score} = S_{\text{category}} (40) + S_{\text{tools}} (25) + S_{\text{style}} (15) + S_{\text{price}} (10) + S_{\text{availability}} (5) + S_{\text{rating}} (5)$$

1. **Category & Specialization (Max 40 pts):**
   - Direct core category match (`AI Video`, `3D & CGI`, etc.): 34 points base.
   - Sub-specialization alignment in brief description: up to +6 points bonus.
   - Specialization keyword hit: 30 points.
   - Portfolio match fallback: 24 points.
2. **Tools & Pipeline Overlap (Max 25 pts):**
   - 1 tool match: 14 points | 2 tools match: 20 points | 3+ tools match: 25 points.
3. **Style & Aesthetic Alignment (Max 15 pts):**
   - Matches brief descriptors against creator style tags and descriptive keywords.
4. **Price vs. Budget Fit (Max 10 pts):**
   - Evaluates creator starting rate against project budget with continuous headroom scaling.
5. **Availability Status (Max 5 pts):**
   - Available: 5.0 pts | Busy: 2.5 pts | Booked: 1.0 pt.
6. **Rating & SLA Score (Max 5 pts):**
   - Combines normalized creator rating (3.0–5.0★) and SLA delivery percentage (70%–100%).

---

## 🔒 Security & Data Protection

- **Password Hashing:** Passlib with `bcrypt` salting.
- **JWT Protection:** Signed tokens (HS256) with expiration controls.
- **Route Authorization:** Enforced via FastAPI dependencies checking active user status and required roles (`brand`, `creator`, `admin`).
- **Workspace Isolation:** Every workspace query strictly verifies that the user is either the assigned recruiter, the assigned creator, or an admin. Third-party users receive HTTP 403 Forbidden.
- **Message Encryption at Rest:** Messages are encrypted before database insertion using symmetric `Fernet` encryption (AES-128-CBC with HMAC).
- **File Upload Safeguards:** Whitelisted file extensions (`jpg`, `jpeg`, `png`, `webp`, `pdf`, `mp4`, `mov`, `zip`), path sanitization against directory traversal, and a 50 MB file size limit.

---

## 🧪 Testing Setup

The codebase includes automated tests in `backend/tests/` and end-to-end verification scripts in `backend/`:
- **Pytest Unit Suite:** Tests authentication, brief generation, community interactions, matching bounds, and workspace isolation using an in-memory SQLite database (`sqlite:///:memory:`).
- **12-Step Lifecycle Script (`test_lifecycle_e2e.py`):** Exercises the complete product flow: Recruiter/Creator Login ➔ Workspace Creation ➔ Deliverable Upload (v1) ➔ Authorized Download ➔ Blocked Unauthorized Download (403) ➔ Blocked Dangerous File Upload (400) ➔ Revision Request ➔ Deliverable Upload (v2 preserving v1) ➔ Blocked Premature Completion (400) ➔ Milestone Release ➔ Project Completion ➔ Verified Review Submission ➔ Blocked Duplicate Review (400).

---

## ⚠️ Current Scope & Transparent Notes

1. **Payment & Escrow Functionality:**
   - Milestone approval and payout releases are implemented as an **architectural state machine simulation** (`pending` ➔ `approved` ➔ `released` ➔ `completed`) to demonstrate the workflow. Direct banking APIs (Razorpay / Stripe Connect) are reserved for the future production roadmap.
2. **Demo Data Note:**
   - The creator directory, portfolio showcases, and historical feed items are seeded demo records designed to showcase the platform's multi-category capabilities and ranking algorithms during the hackathon.
3. **File Storage:**
   - Workspace deliverable files are currently stored on the local container filesystem under `backend/uploads/workspaces/`. Cloud object storage (Amazon S3 / Cloudflare R2) is planned for production scaling.
