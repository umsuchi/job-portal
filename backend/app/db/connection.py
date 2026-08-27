"""Driver connect-args, shared by the app engine and Alembic.

Kept in one place so a TLS or pooling fix lands in both at once.
"""
from __future__ import annotations

import ssl
from typing import Any, Dict

from app.core.config import settings


def build_connect_args() -> Dict[str, Any]:
    """asyncpg connect args for the configured database.

    Two things worth knowing:

    * **TLS.** asyncpg does not understand libpq's ``sslmode``/``channel_binding``
      query arguments, so those are stripped from the URL and TLS is requested
      here instead. The context is built against certifi's CA bundle rather than
      ``ssl=True``, because ``ssl=True`` falls back to the OS trust store — and a
      python.org build on macOS ships without one wired up, which surfaces as
      ``CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate``.
      certifi is already a transitive dependency of httpx, so this costs nothing.
    * **Prepared statements.** Neon's pooled endpoint runs PgBouncer in
      transaction mode, which cannot keep server-side prepared statements alive
      between checkouts. Disabling the statement cache avoids
      ``prepared statement "__asyncpg_stmt_x__" does not exist``.
    """
    if not settings.requires_ssl:
        return {}

    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:  # pragma: no cover - certifi ships with httpx
        context = ssl.create_default_context()

    return {"ssl": context, "statement_cache_size": 0}
