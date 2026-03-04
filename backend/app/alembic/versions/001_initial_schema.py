"""Initial schema — all core tables.

Revision ID: 001
Revises:
Create Date: 2026-03-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. users  (no FK dependencies)
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ------------------------------------------------------------------
    # 2. projects  (FK -> users)
    # ------------------------------------------------------------------
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("platform", sa.String(50), nullable=False, server_default="custom"),
        sa.Column("audience", sa.String(50), nullable=False, server_default="consumers"),
        sa.Column("complexity", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("tone", sa.String(50), nullable=False, server_default="casual"),
        sa.Column("accent_color", sa.String(20), nullable=False, server_default="#00E5FF"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    # ------------------------------------------------------------------
    # 3. sessions  (FK -> projects)
    # ------------------------------------------------------------------
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("stage", sa.String(50), nullable=False, server_default="greeting"),
        sa.Column("messages", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_sessions_project_id", "sessions", ["project_id"])

    # ------------------------------------------------------------------
    # 4. design_sheets  (FK -> projects, one-to-one via unique constraint)
    # ------------------------------------------------------------------
    op.create_table(
        "design_sheets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), unique=True, nullable=False),
        sa.Column("problem", sa.Text, nullable=True),
        sa.Column("audience", sa.String(200), nullable=True),
        sa.Column("mvp", sa.Text, nullable=True),
        sa.Column("features", postgresql.JSONB, nullable=True),
        sa.Column("tone", sa.String(50), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("tech_constraints", sa.Text, nullable=True),
        sa.Column("success_metric", sa.Text, nullable=True),
        sa.Column("confidence_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ------------------------------------------------------------------
    # 5. blocks  (FK -> projects)
    # ------------------------------------------------------------------
    op.create_table(
        "blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=False, server_default="feature"),
        sa.Column("priority", sa.String(10), nullable=False, server_default="mvp"),
        sa.Column("effort", sa.String(5), nullable=False, server_default="M"),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_mvp", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_blocks_project_id", "blocks", ["project_id"])

    # ------------------------------------------------------------------
    # 6. pipeline_nodes  (FK -> projects)
    # ------------------------------------------------------------------
    op.create_table(
        "pipeline_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("layer", sa.String(50), nullable=False),
        sa.Column("selected_tool", sa.String(100), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pipeline_nodes_project_id", "pipeline_nodes", ["project_id"])

    # ------------------------------------------------------------------
    # 7. prompt_kits  (FK -> projects)
    # ------------------------------------------------------------------
    op.create_table(
        "prompt_kits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_prompt_kits_project_id", "prompt_kits", ["project_id"])

    # ------------------------------------------------------------------
    # 8. versions  (FK -> projects)
    # ------------------------------------------------------------------
    op.create_table(
        "versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("snapshot", postgresql.JSONB, nullable=False),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_versions_project_id", "versions", ["project_id"])


def downgrade() -> None:
    # Drop in reverse dependency order (leaf tables first, then root).
    op.drop_table("versions")
    op.drop_table("prompt_kits")
    op.drop_table("pipeline_nodes")
    op.drop_table("blocks")
    op.drop_table("design_sheets")
    op.drop_table("sessions")
    op.drop_table("projects")
    op.drop_table("users")
