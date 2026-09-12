"""create core tables

Revision ID: a1b2c3d4e5f6
Revises: 57223ae2a702
Create Date: 2026-09-12 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "57223ae2a702"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "factories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("industry", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("production_volume", sa.Numeric(), nullable=True),
        sa.Column("production_unit", sa.String(), nullable=True),
        sa.Column("assessment_period", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "processes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("factory_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("process_type", sa.String(), nullable=True),
        sa.Column("production_volume", sa.Numeric(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"], ["factories.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "energy_consumption",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("energy_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["process_id"], ["processes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("material_name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column(
            "recycled_percentage",
            sa.Numeric(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["process_id"], ["processes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "waste",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("waste_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("disposal_method", sa.String(), nullable=False),
        sa.Column(
            "recycled_quantity",
            sa.Numeric(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "landfilled_quantity",
            sa.Numeric(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "reused_quantity",
            sa.Numeric(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["process_id"], ["processes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "emission_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("activity", sa.String(), nullable=False),
        sa.Column("emission_factor", sa.Numeric(), nullable=False),
        sa.Column("emission_factor_source", sa.String(), nullable=True),
        sa.Column("co2e", sa.Numeric(), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["process_id"], ["processes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotspot_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("strategy", sa.String(), nullable=False),
        sa.Column("estimated_cost", sa.String(), nullable=False),
        sa.Column("co2_reduction", sa.Numeric(), nullable=False),
        sa.Column("payback_period", sa.Numeric(), nullable=True),
        sa.Column("score", sa.Numeric(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["hotspot_id"], ["emission_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recommendations")
    op.drop_table("emission_results")
    op.drop_table("waste")
    op.drop_table("materials")
    op.drop_table("energy_consumption")
    op.drop_table("processes")
    op.drop_table("factories")
