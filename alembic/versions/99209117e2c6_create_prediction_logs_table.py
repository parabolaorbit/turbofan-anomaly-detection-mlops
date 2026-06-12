"""create prediction_logs table

Revision ID: 99209117e2c6
Revises: 
Create Date: 2026-05-30 00:15:34.819798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99209117e2c6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "prediction_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("prediction", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("result", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_prediction_logs_id"), "prediction_logs", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_prediction_logs_id"), table_name="prediction_logs")
    op.drop_table("prediction_logs")
