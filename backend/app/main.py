import logging
import os
import shutil
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all models are registered with Base metadata
from app.routes import (
    auth_router,
    creators_router,
    briefs_router,
    community_router,
    workspaces_router,
    shortlist_router,
    leaderboard_router,
    search_router,
    proposals_router,
    notifications_router,
    xero_router,
    licensing_router,
    comparison_router,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("maccall")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes tables on startup and seeds persistent volume if SQLite is empty."""
    logger.info("Checking database configuration...")
    if settings.DATABASE_URL.startswith("sqlite:///"):
        raw_path = settings.DATABASE_URL.replace("sqlite:///", "")
        target_path = Path(raw_path)
        if not target_path.exists():
            candidates = [
                Path("/app/maccall.db"),
                Path("backend/maccall.db"),
                Path("maccall.db"),
                Path(__file__).parent.parent / "maccall.db",
            ]
            for candidate in candidates:
                if candidate.exists() and candidate.resolve() != target_path.resolve():
                    logger.info("Seeding persistent database from %s to %s", candidate, target_path)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(candidate, target_path)
                    break

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

    # Populate baseline dataset if database is brand new and has no users
    from app.database import SessionLocal
    from app.models.users import User
    _init_db = SessionLocal()
    try:
        if _init_db.query(User).count() == 0:
            logger.info("Empty database detected. Populating baseline marketplace data...")
            try:
                from app.seed import seed_database
                seed_database()
                logger.info("Baseline data populated successfully.")
            except Exception as _seed_err:
                logger.warning("Baseline auto-seed failed: %s", _seed_err)

        # Ensure known demo accounts exist with active credentials
        try:
            from app.dependencies import get_password_hash
            from app.models.creators import CreatorProfile
            known_demo_accounts = [
                ("recruiter@codexero.com", "Demo Recruiter", "brand", "Demo@123", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"),
                ("creator@codexero.com", "Demo Content Creator", "creator", "Demo@123", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"),
                ("cleanrecruiter@codexero.com", "Clean Recruiter", "brand", "Demo@123", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80"),
                ("cleancreator@codexero.com", "Clean Content Creator", "creator", "Demo@123", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"),
            ]
            for d_email, d_name, d_role, d_pass, d_avatar in known_demo_accounts:
                existing = _init_db.query(User).filter(User.email == d_email.lower()).first()
                if not existing:
                    u = User(
                        email=d_email.lower(),
                        password_hash=get_password_hash(d_pass),
                        full_name=d_name,
                        role=d_role,
                        avatar_url=d_avatar,
                        bio=f"{d_role.capitalize()} account on KreatorBuzz.",
                        location="Mumbai / London",
                        is_active=True,
                    )
                    _init_db.add(u)
                    _init_db.commit()
                    _init_db.refresh(u)
                else:
                    u = existing
                    # Ensure active status and proper credentials
                    u.is_active = True
                    u.password_hash = get_password_hash(d_pass)
                    _init_db.commit()
                    _init_db.refresh(u)

                if d_role == "creator":
                    prof = _init_db.query(CreatorProfile).filter(CreatorProfile.user_id == u.id).first()
                    if not prof:
                        prof = CreatorProfile(
                            user_id=u.id,
                            display_name=u.full_name,
                            tagline="AI Visual Artist & Cinema Director",
                            specialization="Cinematic Video & Luxury",
                            skills=["Prompt Engineering", "Visual Direction", "Post-Production"],
                            ai_tools=["Midjourney v6", "Runway Gen-3", "ComfyUI"],
                            starting_rate=50000.0,
                            delivery_days=5,
                            commercial_rights=True,
                            availability_status="available",
                            rating=5.0,
                            sla_score=99.0,
                            on_time_percentage=100.0,
                            location=u.location,
                        )
                        _init_db.add(prof)
                        _init_db.commit()
        except Exception as _demo_err:
            logger.warning("Error ensuring known demo accounts: %s", _demo_err)
    except Exception as _check_err:
        logger.warning("Database user count check error: %s", _check_err)
    finally:
        _init_db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="KreatorBuzz AI Creator Marketplace Backend API — Create Your Own Buzz",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(creators_router, prefix=settings.API_V1_STR)
app.include_router(briefs_router, prefix=settings.API_V1_STR)
app.include_router(community_router, prefix=settings.API_V1_STR)
app.include_router(workspaces_router, prefix=settings.API_V1_STR)
app.include_router(shortlist_router, prefix=settings.API_V1_STR)
app.include_router(leaderboard_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(proposals_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(xero_router, prefix=settings.API_V1_STR)
app.include_router(licensing_router, prefix=settings.API_V1_STR)
app.include_router(comparison_router, prefix=settings.API_V1_STR)



@app.get("/health")
def health_check():
    """Health check endpoint for orchestration."""
    return {"status": "healthy"}


# Locate built frontend if available
FRONTEND_DIST: Path | None = None
possible_dist_dirs = [
    Path("/app/frontend/dist"),
    Path("/app/dist"),
    Path(__file__).parent.parent.parent / "frontend" / "dist",
    Path("frontend/dist"),
    Path("../frontend/dist"),
]
for p in possible_dist_dirs:
    if p.exists() and (p / "index.html").exists():
        FRONTEND_DIST = p
        break

if FRONTEND_DIST:
    logger.info("Serving frontend static assets from %s", FRONTEND_DIST)
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path in ("health", "docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def root():
        """Root health and platform status endpoint."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
        }

