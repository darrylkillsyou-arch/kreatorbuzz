# Architecture Documentation — Maccall Platform

## 1. System Architecture Overview

The Maccall platform utilizes a decoupled client-server architecture styled around a cohesive **Warm Editorial Luxury** design system.

```
┌─────────────────────────────────────────────────────────────┐
│                 Vite + React 18 Frontend                   │
│        (Tailwind CSS, EB Garamond, Plus Jakarta Sans)       │
│                                                             │
│  /discover  /community  /briefs  /workspaces  /leaderboard  │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API (JWT Bearer)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│                                                             │
│ ┌───────────────┐ ┌───────────────┐ ┌────────────────────┐ │
│ │  Auth & RBAC  │ │ Brief Engine  │ │  Matching Engine   │ │
│ └───────────────┘ └───────────────┘ └────────────────────┘ │
│ ┌───────────────┐ ┌───────────────┐ ┌────────────────────┐ │
│ │  Workspaces   │ │  Community    │ │ Storage Encryption │ │
│ └───────────────┘ └───────────────┘ └────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy 2.0 ORM
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             SQLite (Default) / PostgreSQL DB                │
│       Users, Profiles, Portfolios, Briefs, Messages,        │
│          Workspaces, Milestones, Community Posts            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Design System Tokens & Integrity

The visual identity strictly enforces the approved **Warm Editorial Luxury** specifications:

- **Canvas & Backgrounds:** Base canvas `#F9F8F5` (champagne ivory) layered over `#F4F2EB` (alabaster parchment) and `#F0EEE7`. Pure `#FFFFFF` is restricted to active floating sheets.
- **Typography:** 
  - `EB Garamond` for Display, Headlines, and Section Titles.
  - `Plus Jakarta Sans` for reading body copy, metadata indicators, and interactive labels.
- **Dark Solids & Ink:** `#1A1917` (deep espresso-noir) for primary structural typography and buttons.
- **Accents:** `#785923` and `#A68248` (antiqued bronze/gold) for verification badges, active pill borders, and highlight accents.

---

## 3. Data Model Architecture

The database entities are partitioned by domain concerns:

### `app.models.users`
- `User`: Handles identity, bcrypt hashed credentials, avatar, and roles (`brand`, `creator`, `admin`).

### `app.models.creators`
- `CreatorProfile`: Contains editorial introduction, specialization (Video, Fashion, 3D Motion, Sonic, Brand), skills array, toolstack (Runway, Sora, Kling, Midjourney, Flux, ElevenLabs, ComfyUI), starting rates, turnaround velocity, rating, SLA performance metrics, and tier-1 verification status.
- `PortfolioItem`: High-res commercial and experimental pieces tagged by visual category and generation pipeline.
- `CreatorAchievement`: Archival laurels (e.g., *Director of the Month*, *Maison Fellow*, *Spatial Pioneer*).
- `Verification`: Multi-point cryptographic verification signals (Identity, Tools, Portfolio, Workflow, Commercial Rights).

### `app.models.briefs`
- `Brief`: Structured campaign requirement records generated either via the AI Brief Builder or manual authoring. Tracks objective, style paradigm, deliverables, distribution channels, budget boundaries, turnaround SLA, and commercial indemnity buyout terms.

### `app.models.community`
- `CommunityPost`: Salon dispatches supporting 6 post categories (`showcase`, `creator_request`, `service`, `collaboration`, `open_brief`, `achievement`).
- `PostLike`, `PostComment`, `Follow`, `SavedPost`: Community engagement mechanics with immediate creator discovery hooks.

### `app.models.workspaces`
- `Workspace`: Private production rooms dedicated to a brand and director pair.
- `WorkspaceMilestone`: Escrow tranche records (`pending`, `in_review`, `approved`, `released`) with financial valuation.
- `WorkspaceMessage`: Stored with symmetric encryption at rest (AES-128-CBC / HMAC-SHA256 via Fernet).
- `SharedFile`: Tracked production deliverables (4K ProRes master cuts, raw LoRA checkpoints, ambisonic stems).
- `RevisionRequest`: Structured feedback loops tied to specific production milestones.

### `app.models.shortlist` & `app.models.leaderboard`
- `Shortlist`: Bookmarking records connecting brands to potential director folios.
- `LeaderboardEntry`: Weekly and monthly ranked consensus entries based on verified deliverability, escrow integrity, and client ratings.

---

## 4. Intelligent Algorithms

### A. AI Brief Synthesizer (`app.services.brief_generator`)
Converts unformatted brand prompts into structured JSON.
- **Primary:** Google Gemini API (`gemini-2.5-flash` via `google-genai`).
- **Offline Fallback:** Heuristic keyword classifier extracting objectives, style paradigms, aspect ratios, suggested models, deliverables, and estimated budgets without requiring API credentials.

### B. Creator Matching Engine (`app.services.matching`)
Calculates a 0–100 `MatchScore` with explicit itemized rationale:
1. **Style & Specialization Fit** (30% weight)
2. **AI Toolstack Overlap** (20% weight)
3. **Skills Alignment** (15% weight)
4. **Immediate Availability Capacity** (10% weight)
5. **Turnaround SLA Compatibility** (10% weight)
6. **Commercial IP Licensing Support** (10% weight)
7. **Portfolio Track Record** (5% weight)

### C. Message Encryption at Rest (`app.services.encryption`)
Uses Cryptography Fernet to encrypt private communications before persisting to the database. Decryption is performed in-memory exclusively for authorized workspace members.
