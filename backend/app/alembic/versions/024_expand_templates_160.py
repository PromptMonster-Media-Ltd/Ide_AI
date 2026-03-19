"""Replace all system templates with 160 templates across 16 concept categories.

Revision ID: 024
Revises: 023
Create Date: 2026-03-19
"""
import json
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "024"
down_revision: Union[str, None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove all existing system templates
    op.execute(sa.text(
        "DELETE FROM project_templates WHERE is_system = true"
    ))

    # Load the expanded 160-template seed file
    seed_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "project_templates.seed.json"
    )
    with open(seed_path, encoding="utf-8") as f:
        templates = json.load(f)

    for t in templates:
        op.execute(
            sa.text(
                "INSERT INTO project_templates (id, name, description, icon, category, concept_sheet, is_system, created_at) "
                "VALUES (gen_random_uuid(), :name, :description, :icon, :category, CAST(:cs AS jsonb), true, now()) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(
                name=t["name"],
                description=t["description"],
                icon=t["icon"],
                category=t["category"],
                cs=json.dumps(t.get("concept_sheet", {})),
            )
        )


def downgrade() -> None:
    # Remove the 160 templates (restoring old ones would require re-running 017+018)
    op.execute(sa.text(
        "DELETE FROM project_templates WHERE is_system = true"
    ))
