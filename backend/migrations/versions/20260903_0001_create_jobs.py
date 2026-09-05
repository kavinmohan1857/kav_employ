"""create jobs table

Revision ID: 20260903_0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("raw_title", sa.String(length=300), nullable=False),
        sa.Column("normalized_title", sa.String(length=200), nullable=False),
        sa.Column("raw_company", sa.String(length=300), nullable=False),
        sa.Column("normalized_company", sa.String(length=300), nullable=False),
        sa.Column("raw_location", sa.String(length=300), nullable=False),
        sa.Column("normalized_location", sa.String(length=300), nullable=False),
        sa.Column("workplace_type", sa.String(length=30), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_external_id", sa.String(length=300), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("date_posted", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("employment_type", sa.String(length=30), nullable=True),
        sa.Column("minimum_years_experience", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("maximum_years_experience", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(length=3), nullable=True),
        sa.Column("entry_level_score", sa.Integer(), nullable=False),
        sa.Column("entry_level_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("classifier_version", sa.String(length=30), nullable=False),
        sa.Column("duplicate_fingerprint", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "entry_level_score BETWEEN 0 AND 100", name="ck_jobs_entry_level_score_range"
        ),
        sa.CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
        sa.CheckConstraint(
            "minimum_years_experience IS NULL OR maximum_years_experience IS NULL "
            "OR minimum_years_experience <= maximum_years_experience",
            name="ck_jobs_experience_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_duplicate_fingerprint", "jobs", ["duplicate_fingerprint"])
    op.create_index("ix_jobs_normalized_company", "jobs", ["normalized_company"])
    op.create_index("ix_jobs_normalized_location", "jobs", ["normalized_location"])
    op.create_index("ix_jobs_normalized_title", "jobs", ["normalized_title"])


def downgrade() -> None:
    op.drop_index("ix_jobs_normalized_title", table_name="jobs")
    op.drop_index("ix_jobs_normalized_location", table_name="jobs")
    op.drop_index("ix_jobs_normalized_company", table_name="jobs")
    op.drop_index("ix_jobs_duplicate_fingerprint", table_name="jobs")
    op.drop_table("jobs")
