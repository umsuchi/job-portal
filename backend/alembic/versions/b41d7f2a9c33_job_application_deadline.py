"""job application deadline

Adds an optional, inclusive application deadline to job posts.

DATE rather than TIMESTAMPTZ on purpose: deadlines are stated as days ("apply by
15 March"), and a timestamp would invent a precision recruiters never gave while
reading differently in every timezone.

No partial index on the deadline: the predicate a browse query needs compares
against the current date, and `CURRENT_DATE` is not immutable, so Postgres will
not accept it in an index predicate. The existing partial index on open jobs
still does the narrowing.

Revision ID: b41d7f2a9c33
Revises: 0c609d6cdfda
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b41d7f2a9c33'
down_revision: Union[str, None] = '0c609d6cdfda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('application_deadline', sa.Date(), nullable=True))
    # Existing posts have no deadline, which the model reads as "never expires" —
    # so nothing that was applicable yesterday stops being applicable today.
    op.create_index(
        'ix_jobs_application_deadline', 'jobs', ['application_deadline'],
        unique=False, postgresql_where=sa.text('application_deadline IS NOT NULL'),
    )


def downgrade() -> None:
    op.drop_index('ix_jobs_application_deadline', table_name='jobs')
    op.drop_column('jobs', 'application_deadline')
