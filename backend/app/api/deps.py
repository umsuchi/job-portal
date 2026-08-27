"""Shared FastAPI dependencies: DB session, current user, role gates."""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenError, decode_token
from app.db.session import get_db
from app.models.user import ROLE_CANDIDATE, ROLE_RECRUITER, User

bearer_scheme = HTTPBearer(auto_error=False)
optional_bearer = HTTPBearer(auto_error=False)

CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def _user_from_token(token: str, db: AsyncSession) -> User:
    try:
        payload = decode_token(token, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
    except (TokenError, KeyError, ValueError):
        raise CREDENTIALS_EXC
    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise CREDENTIALS_EXC
    return user


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if creds is None:
        raise CREDENTIALS_EXC
    return await _user_from_token(creds.credentials, db)


async def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """For public endpoints that enrich their response when a token is present."""
    if creds is None:
        return None
    try:
        return await _user_from_token(creds.credentials, db)
    except HTTPException:
        return None


async def require_candidate(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_CANDIDATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to candidates.",
        )
    return user


async def require_recruiter(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to recruiters.",
        )
    return user
