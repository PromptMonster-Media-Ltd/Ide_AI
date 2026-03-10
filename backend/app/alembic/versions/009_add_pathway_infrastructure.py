"""Add pathway infrastructure: pathway_id, fields_data, module_artifacts table.

Revision ID: 009
Revises: 008
Create Date: 2026-03-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add pathway_id to projects table
    op.add_column(
        "projects",
        sa.Column("pathway_id", sa.String(50), nullable=False, server_default="software_product"),
    )

    # 2. Add fields_data to design_sheets table
    op.add_column(
        "design_sheets",
        sa.Column("fields_data", postgresql.JSONB(), nullable=True, server_default="{}"),
    )

    # 3. Create module_artifacts table
    op.create_table(
        "module_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("module_id", sa.String(50), nullable=False),
        sa.Column("artifact_type", sa.String(50), nullable=False),
        sa.Column("data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_module_artifacts_project_module", "module_artifacts", ["project_id", "module_id"])


def downgrade() -> None:
    op.drop_index("ix_module_artifacts_project_module", table_name="module_artifacts")
    op.drop_table("module_artifacts")
    op.drop_column("design_sheets", "fields_data")
    op.drop_column("projects", "pathway_id")
