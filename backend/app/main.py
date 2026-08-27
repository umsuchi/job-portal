"""FastAPI entrypoint — one monolith, five routers (spec §3)."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import applications, auth, jobs, messages, suggestions
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Job Portal API",
    version="1.0.0",
    description=(
        "Recruiters post jobs, candidates browse and apply, both sides message "
        "on an application, and candidates get AI-ranked suggestions."
    ),
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(messages.router)
app.include_router(suggestions.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.env}


@app.get("/", tags=["meta"])
async def root():
    return {"service": "job-portal-api", "docs": "/docs"}
