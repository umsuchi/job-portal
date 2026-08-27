"""initial schema

Revision ID: 155af6724924
Revises:
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '155af6724924'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('candidate', 'recruiter')", name='ck_users_role'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'candidate_profiles',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('resume_url', sa.String(length=1024), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
    )

    op.create_table(
        'recruiter_profiles',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('company_website', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
    )

    op.create_table(
        'jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('recruiter_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('required_skills', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('job_type', sa.String(length=30), nullable=False),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='open', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "job_type IN ('full_time', 'part_time', 'contract', 'internship', 'remote')",
            name='ck_jobs_job_type',
        ),
        sa.CheckConstraint("status IN ('open', 'closed')", name='ck_jobs_status'),
        sa.CheckConstraint(
            'salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max',
            name='ck_jobs_salary_range',
        ),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    # Partial: the browse list only ever reads open jobs.
    op.create_index(
        'ix_jobs_open_created_at', 'jobs', ['created_at'],
        unique=False, postgresql_where=sa.text("status = 'open'"),
    )
    op.create_index(op.f('ix_jobs_recruiter_id'), 'jobs', ['recruiter_id'], unique=False)
    # GIN: powers `required_skills && :candidate_skills` (spec section 12).
    op.create_index(
        'ix_jobs_required_skills_gin', 'jobs', ['required_skills'],
        unique=False, postgresql_using='gin',
    )

    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('cover_note', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='applied', nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('applied', 'reviewed', 'shortlisted', 'rejected', 'hired', 'withdrawn')",
            name='ck_applications_status',
        ),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'candidate_id', name='uq_applications_job_candidate'),
    )
    op.create_index(op.f('ix_applications_applied_at'), 'applications', ['applied_at'], unique=False)
    op.create_index(op.f('ix_applications_candidate_id'), 'applications', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=False),
        sa.Column('receiver_id', sa.UUID(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_application_sent_at', 'messages', ['application_id', 'sent_at'], unique=False)
    op.create_index(
        'ix_messages_receiver_unread', 'messages', ['receiver_id'],
        unique=False, postgresql_where=sa.text('read_at IS NULL'),
    )
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)

    op.create_table(
        'suggestion_caches',
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('skills_hash', sa.String(length=64), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('candidate_id'),
    )


def downgrade() -> None:
    op.drop_table('suggestion_caches')
    op.drop_index('ix_messages_sender_id', table_name='messages')
    op.drop_index('ix_messages_receiver_unread', table_name='messages',
                  postgresql_where=sa.text('read_at IS NULL'))
    op.drop_index('ix_messages_application_sent_at', table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_candidate_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_applied_at'), table_name='applications')
    op.drop_table('applications')
    op.drop_index('ix_jobs_required_skills_gin', table_name='jobs', postgresql_using='gin')
    op.drop_index(op.f('ix_jobs_recruiter_id'), table_name='jobs')
    op.drop_index('ix_jobs_open_created_at', table_name='jobs',
                  postgresql_where=sa.text("status = 'open'"))
    op.drop_table('jobs')
    op.drop_table('recruiter_profiles')
    op.drop_table('candidate_profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
