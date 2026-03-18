"""Widen avatar_url column from VARCHAR(500) to TEXT to support base64 data URIs."""

from alembic import op
import sqlalchemy as sa

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "avatar_url",
        type_=sa.Text(),
        existing_type=sa.String(500),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "avatar_url",
        type_=sa.String(500),
        existing_type=sa.Text(),
        existing_nullable=True,
    )
