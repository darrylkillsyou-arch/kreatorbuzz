# API Documentation — Maccall Platform

Base URL: `http://localhost:8000/api`

All protected endpoints require an `Authorization: Bearer <token>` header.

---

## 1. Authentication Endpoints

### `POST /api/auth/register`
Create a new Brand or Creator account.
- **Request Body**:
  ```json
  {
    "email": "director@atelier.com",
    "password": "securepassword123",
    "full_name": "Aarav Studio",
    "role": "creator",
    "location": "Milan / Paris"
  }
  ```
- **Response**: `200 OK` with user profile and JWT `access_token`.

### `POST /api/auth/login`
Authenticate with email and password.
- **Request Body**:
  ```json
  {
    "email": "brand@maccall.demo",
    "password": "demo1234"
  }
  ```
- **Response**: `200 OK` with JWT `access_token` and user record.

### `GET /api/auth/me` *(Protected)*
Retrieve current authenticated user details and active role.

---

## 2. Creator Directory Endpoints

### `GET /api/creators`
List all verified AI creators.
- **Query Parameters**:
  - `category`: `all`, `video`, `fashion`, `3d`, `audio`, `brand`
  - `query`: Free-text search across bio, name, skills, and tools
  - `limit`, `offset`

### `GET /api/creators/{id}`
Retrieve a creator's profile, including portfolio items, verified tools, SLA scores, and verification signals.

### `GET /api/creators/{id}/portfolio`
Retrieve full portfolio items for a specific creator.

---

## 3. Brief & AI Synthesizer Endpoints

### `POST /api/briefs/generate`
Synthesize an unformatted natural language prompt into an actionable, editable creative brief.
- **Request Body**:
  ```json
  {
    "prompt": "I need a 30s kinetic runway video for a luxury car in brutalist dusk illumination"
  }
  ```
- **Response**: Structured brief JSON with objectives, style tags, distribution channels, deliverables, suggested tools, estimated budget, and turnaround SLA.

### `POST /api/briefs` *(Protected)*
Save a new brief.

### `GET /api/briefs` *(Protected)*
List all briefs authored by the current brand.

### `GET /api/briefs/{id}` *(Protected)*
Retrieve detailed brief specifications.

### `POST /api/briefs/{id}/match-creators` *(Protected)*
Run the multi-factor matching engine against a brief and return ranked creators with match scores (0–100) and rationale.

---

## 4. Workspaces & Collaboration Endpoints

### `GET /api/workspaces` *(Protected)*
List production workspaces where the current user is a member.

### `GET /api/workspaces/{id}` *(Protected)*
Retrieve workspace details: milestones, deliverables, members, and status (`discovery`, `brief_approved`, `production`, `review`, `delivered`).

### `POST /api/workspaces` *(Protected)*
Create a new workspace between a brand and creator based on an approved brief.

### `GET /api/workspaces/{id}/messages` *(Protected)*
Retrieve decrypted messages for the workspace.

### `POST /api/workspaces/{id}/messages` *(Protected)*
Send a message. Stored encrypted at rest using symmetric key.

### `PUT /api/workspaces/{id}/milestones/{milestone_id}` *(Protected)*
Update milestone status (`approved`, `in_review`, `released`) or approve tranche release.

### `POST /api/workspaces/{id}/revision-requests` *(Protected)*
Submit a structured revision request on a milestone.

---

## 5. Community Salon Endpoints

### `GET /api/community/posts`
List community dispatches with author details, tags, like counts, and comment counts.
- **Query Parameters**: `post_type`, `limit`, `offset`

### `POST /api/community/posts` *(Protected)*
Publish a showcase, service offering, open brief, or collaboration request.

### `POST /api/community/posts/{id}/like` *(Protected)*
Toggle like on a community post.

### `POST /api/community/posts/{id}/comment` *(Protected)*
Add a comment to a discussion thread.

---

## 6. Shortlist & Leaderboard Endpoints

### `GET /api/shortlist` *(Protected)*
Get the brand's bookmarked creators.

### `POST /api/shortlist` *(Protected)*
Bookmark a creator folio.

### `POST /api/shortlist/{id}/hire` *(Protected)*
Directly initiate a commission and spawn a dedicated production workspace.

### `GET /api/leaderboard`
Retrieve the verified director rankings, SLA indices, and curator selections.
