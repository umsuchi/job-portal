"""richer job posts and candidate profiles

Adds the structured job detail (responsibilities, requirements, benefits,
nice-to-have skills, seniority) and the candidate fields the suggestion engine
scores against (experience, preferences, avatars).

The one non-additive part: `job_type` used to mix employment type with work
arrangement — "remote" sat alongside "full_time". Work arrangement moves to its
own `work_mode` column, so existing `job_type='remote'` rows are rewritten to
`full_time` + `work_mode='remote'` before the check constraint is tightened.
That reading is a guess for rows created under the old schema; it is the only
one available, and it is the common case.

Revision ID: 0c609d6cdfda
Revises: 155af6724924
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0c609d6cdfda'
down_revision: Union[str, None] = '155af6724924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JOB_TYPES = ("full_time", "part_time", "contract", "internship", "temporary")
OLD_JOB_TYPES = ("full_time", "part_time", "contract", "internship", "remote")
WORK_MODES = ("onsite", "hybrid", "remote")
EXPERIENCE_LEVELS = ("entry", "junior", "mid", "senior", "lead", "principal")


def _in(column: str, values: Sequence[str]) -> str:
    return f"{column} IN (" + ", ".join(f"'{v}'" for v in values) + ")"


def upgrade() -> None:
    # ---------------------------------------------------------- candidates
    op.add_column('candidate_profiles', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('candidate_profiles', sa.Column('avatar_url', sa.String(length=1024), nullable=True))
    op.add_column('candidate_profiles', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('candidate_profiles', sa.Column('years_experience', sa.Integer(), nullable=True))
    op.add_column('candidate_profiles', sa.Column('experience_level', sa.String(length=20), nullable=True))
    op.add_column('candidate_profiles', sa.Column('preferred_job_types', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('candidate_profiles', sa.Column('preferred_work_modes', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('candidate_profiles', sa.Column('preferred_locations', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('candidate_profiles', sa.Column('desired_salary_min', sa.Integer(), nullable=True))
    op.add_column('candidate_profiles', sa.Column('open_to_work', sa.Boolean(), server_default='true', nullable=False))

    op.create_check_constraint(
        'ck_candidate_experience_level', 'candidate_profiles',
        f"experience_level IS NULL OR {_in('experience_level', EXPERIENCE_LEVELS)}",
    )
    op.create_check_constraint(
        'ck_candidate_years_experience', 'candidate_profiles',
        'years_experience IS NULL OR years_experience >= 0',
    )

    # ---------------------------------------------------------- recruiters
    op.add_column('recruiter_profiles', sa.Column('avatar_url', sa.String(length=1024), nullable=True))
    op.add_column('recruiter_profiles', sa.Column('about', sa.Text(), nullable=True))
    op.add_column('recruiter_profiles', sa.Column('industry', sa.String(length=120), nullable=True))
    op.add_column('recruiter_profiles', sa.Column('headquarters', sa.String(length=255), nullable=True))

    # --------------------------------------------------------------- jobs
    op.add_column('jobs', sa.Column('responsibilities', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('jobs', sa.Column('requirements', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('jobs', sa.Column('benefits', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('jobs', sa.Column('nice_to_have_skills', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False))
    op.add_column('jobs', sa.Column('experience_level', sa.String(length=20), server_default='mid', nullable=False))
    op.add_column('jobs', sa.Column('min_years_experience', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('work_mode', sa.String(length=20), server_default='onsite', nullable=False))
    op.add_column('jobs', sa.Column('salary_currency', sa.String(length=3), server_default='USD', nullable=False))

    op.create_index(
        'ix_jobs_nice_to_have_skills_gin', 'jobs', ['nice_to_have_skills'],
        unique=False, postgresql_using='gin',
    )

    # Backfill BEFORE tightening the constraint, or the old rows fail it.
    op.execute(
        "UPDATE jobs SET work_mode = 'remote', job_type = 'full_time' "
        "WHERE job_type = 'remote'"
    )

    op.drop_constraint('ck_jobs_job_type', 'jobs', type_='check')
    op.create_check_constraint('ck_jobs_job_type', 'jobs', _in('job_type', JOB_TYPES))
    op.create_check_constraint('ck_jobs_work_mode', 'jobs', _in('work_mode', WORK_MODES))
    op.create_check_constraint(
        'ck_jobs_experience_level', 'jobs', _in('experience_level', EXPERIENCE_LEVELS)
    )
    op.create_check_constraint(
        'ck_jobs_min_years', 'jobs',
        'min_years_experience IS NULL OR min_years_experience >= 0',
    )


def downgrade() -> None:
    op.drop_constraint('ck_jobs_min_years', 'jobs', type_='check')
    op.drop_constraint('ck_jobs_experience_level', 'jobs', type_='check')
    op.drop_constraint('ck_jobs_work_mode', 'jobs', type_='check')
    op.drop_constraint('ck_jobs_job_type', 'jobs', type_='check')

    # Fold work_mode back into job_type, losing the distinction again.
    op.execute("UPDATE jobs SET job_type = 'remote' WHERE work_mode = 'remote'")
    # 'temporary' has no pre-split equivalent; the closest is a contract.
    op.execute("UPDATE jobs SET job_type = 'contract' WHERE job_type = 'temporary'")
    op.create_check_constraint('ck_jobs_job_type', 'jobs', _in('job_type', OLD_JOB_TYPES))

    op.drop_index('ix_jobs_nice_to_have_skills_gin', table_name='jobs', postgresql_using='gin')
    for column in ('salary_currency', 'work_mode', 'min_years_experience',
                   'experience_level', 'nice_to_have_skills', 'benefits',
                   'requirements', 'responsibilities'):
        op.drop_column('jobs', column)

    for column in ('headquarters', 'industry', 'about', 'avatar_url'):
        op.drop_column('recruiter_profiles', column)

    op.drop_constraint('ck_candidate_years_experience', 'candidate_profiles', type_='check')
    op.drop_constraint('ck_candidate_experience_level', 'candidate_profiles', type_='check')
    for column in ('open_to_work', 'desired_salary_min', 'preferred_locations',
                   'preferred_work_modes', 'preferred_job_types', 'experience_level',
                   'years_experience', 'location', 'avatar_url', 'bio'):
        op.drop_column('candidate_profiles', column)
