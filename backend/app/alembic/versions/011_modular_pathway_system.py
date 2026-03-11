"""Add modular pathway system: categories on projects, module_pathways and module_responses tables.

Revision ID: 011
Revises: 010
Create Date: 2026-03-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Add category columns to projects ---
    op.add_column(
        "projects",
        sa.Column("primary_category", sa.String(50), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("secondary_category", sa.String(50), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("pathway_locked", sa.Boolean(), nullable=False, server_default="false"),
    )

    # --- Create module_pathways table ---
    op.create_table(
        "module_pathways",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modules", JSONB, nullable=False, server_default="[]"),
        sa.Column("lite_deep_settings", JSONB, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_module_pathways_project_id", "module_pathways", ["project_id"])

    # --- Create module_responses table ---
    op.create_table(
        "module_responses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.String(50), nullable=False),
        sa.Column("responses", JSONB, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_module_responses_project_module", "module_responses", ["project_id", "module_id"])


def downgrade() -> None:
    op.drop_table("module_responses")
    op.drop_table("module_pathways")
    op.drop_column("projects", "pathway_locked")
    op.drop_column("projects", "secondary_category")
    op.drop_column("projects", "primary_category")
