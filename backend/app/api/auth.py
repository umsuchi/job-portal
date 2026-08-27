"""EP-1 — registration, login, refresh, profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.suggestion import SuggestionCache
from app.models.user import (
    ROLE_CANDIDATE,
    CandidateProfile,
    RecruiterProfile,
    User,
)
from app.schemas.auth import (
    AccessToken,
    LoginRequest,
    ProfileUpdate,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _access_ttl_seconds() -> int:
    return settings.access_token_expire_minutes * 60


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """US-1.1 — create an account with a bcrypt-hashed password and a profile row."""
    email = payload.email.lower().strip()
    existing = await db.scalar(select(User.id).where(User.email == email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()

    if payload.role == ROLE_CANDIDATE:
        db.add(
            CandidateProfile(
                user_id=user.id, full_name=payload.full_name, skills=[]
            )
        )
    else:
        db.add(
            RecruiterProfile(user_id=user.id, company_name=payload.company_name)
        )

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """US-1.2 — exchange credentials for an access + refresh pair."""
    user = await db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    # Same message either way so the endpoint cannot be used to enumerate emails.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    subject = str(user.id)
    return TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
        expires_in=_access_ttl_seconds(),
    )


@router.post("/refresh", response_model=AccessToken)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """US-1.3 — mint a new access token from a valid refresh token."""
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    user = await db.scalar(select(User.id).where(User.id == claims["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account no longer exists."
        )
    return AccessToken(
        access_token=create_access_token(claims["sub"]), expires_in=_access_ttl_seconds()
    )


@router.get("/me", response_model=UserOut)
async def read_me(user: User = Depends(get_current_user)):
    """US-1.4 — current user plus the profile matching their role."""
    return user


@router.put("/me", response_model=UserOut)
async def update_me(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """US-1.4 — update the caller's own profile.

    Changing a candidate's skills drops their cached suggestions so the next
    dashboard load regenerates against the new skill set (US-5.3).
    """
    data = payload.model_dump(exclude_unset=True)

    if user.is_candidate:
        profile = user.candidate_profile
        if profile is None:
            profile = CandidateProfile(user_id=user.id, skills=[])
            db.add(profile)
            await db.flush()
        skills_changed = "skills" in data and data["skills"] != list(profile.skills or [])
        for field in ("full_name", "headline", "skills", "resume_url"):
            if field in data:
                setattr(profile, field, data[field])
        if skills_changed:
            cache = await db.get(SuggestionCache, user.id)
            if cache is not None:
                await db.delete(cache)
    else:
        profile = user.recruiter_profile
        if profile is None:
            profile = RecruiterProfile(user_id=user.id)
            db.add(profile)
            await db.flush()
        for field in ("company_name", "company_website"):
            if field in data:
                setattr(profile, field, data[field])

    await db.commit()
    await db.refresh(user)
    return user
