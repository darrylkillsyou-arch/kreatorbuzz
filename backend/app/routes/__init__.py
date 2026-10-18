from app.routes.auth import router as auth_router
from app.routes.creators import router as creators_router
from app.routes.briefs import router as briefs_router
from app.routes.community import router as community_router
from app.routes.workspaces import router as workspaces_router
from app.routes.shortlist import router as shortlist_router
from app.routes.leaderboard import router as leaderboard_router
from app.routes.search import router as search_router
from app.routes.proposals import router as proposals_router
from app.routes.notifications import router as notifications_router
from app.routes.xero import router as xero_router

__all__ = [
    "auth_router",
    "creators_router",
    "briefs_router",
    "community_router",
    "workspaces_router",
    "shortlist_router",
    "leaderboard_router",
    "search_router",
    "proposals_router",
    "notifications_router",
    "xero_router",
]

