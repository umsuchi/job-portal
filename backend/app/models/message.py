"""Messages, scoped to a single application thread (spec §9, FR-7)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_application_sent_at", "application_id", "sent_at"),
        # Serves the unread badge. Partial, because the only rows it ever
        # has to find are the unread ones.
        Index(
            "ix_messages_receiver_unread",
            "receiver_id",
            postgresql_where=text("read_at IS NULL"),
        ),
        # Postgres does not index foreign keys automatically; this one is
        # needed for the ON DELETE CASCADE from users.
        Index("ix_messages_sender_id", "sender_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    application_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    application: Mapped["Application"] = relationship(back_populates="messages")  # noqa: F821
