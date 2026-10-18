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
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Maccall AI Creator Marketplace Backend API",
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

