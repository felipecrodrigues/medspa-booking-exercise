"""Create the initial medspa booking schema."""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_booking_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "medspas",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("phone_number", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("medspa_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.CheckConstraint("duration > 0", name="ck_services_duration_positive"),
        sa.CheckConstraint(
            "name ~ '[^[:space:]]'",
            name="ck_services_name_nonblank",
        ),
        sa.CheckConstraint("price >= 0", name="ck_services_price_nonnegative"),
        sa.ForeignKeyConstraint(["medspa_id"], ["medspas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_services_medspa_id", "services", ["medspa_id"])
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("medspa_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'scheduled'"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('scheduled', 'completed', 'canceled')",
            name="ck_appointments_status_allowed",
        ),
        sa.ForeignKeyConstraint(["medspa_id"], ["medspas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_medspa_id", "appointments", ["medspa_id"])
    op.create_table(
        "appointment_services",
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("price_at_booking", sa.Integer(), nullable=False),
        sa.Column("duration_at_booking", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "duration_at_booking > 0",
            name="ck_appointment_services_duration_positive",
        ),
        sa.CheckConstraint(
            "price_at_booking >= 0",
            name="ck_appointment_services_price_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["appointment_id"], ["appointments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("appointment_id", "service_id"),
    )


def downgrade() -> None:
    op.drop_table("appointment_services")
    op.drop_index("ix_appointments_medspa_id", table_name="appointments")
    op.drop_table("appointments")
    op.drop_index("ix_services_medspa_id", table_name="services")
    op.drop_table("services")
    op.drop_table("medspas")
