"""API route modules."""

from src.api.routes.auth import router as auth_router, profile_router
from src.api.routes.tasks import router as tasks_router
from src.api.routes.categories import router as categories_router
from src.api.routes.tags import router as tags_router

__all__ = [
    "auth_router",
    "profile_router",
    "tasks_router",
    "categories_router",
    "tags_router",
]
