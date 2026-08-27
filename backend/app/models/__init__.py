"""Model package — importing this registers every table on Base.metadata."""
from app.models.application import Application  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.suggestion import SuggestionCache  # noqa: F401
from app.models.user import CandidateProfile, RecruiterProfile, User  # noqa: F401

__all__ = [
    "Application",
    "CandidateProfile",
    "Job",
    "Message",
    "RecruiterProfile",
    "SuggestionCache",
    "User",
]
