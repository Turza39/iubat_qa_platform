from .answers import router as answers_router
from .questions import router as questions_router
from .users import router as users_router
from .votes import router as votes_router

__all__ = ["answers_router", "questions_router", "users_router", "votes_router"]
