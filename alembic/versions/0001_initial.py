"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = postgresql.ENUM(
    "CHEF_AGENCE", "AGENT", "COORDINATEUR", name="user_role_enum", create_type=False
)
zone_enum = postgresql.ENUM(
    "Tunis", "La Marsa", "Carthage", "Gammarth", "Sidi Bou Saïd",
    "La Goulette", "Le Bardo", "Ariana", "Ben Arous", "Manouba",
    name="zone_enum", create_type=False
)
property_type_enum = postgresql.ENUM(
    "Appartement", "Villa", "Studio", "Local commercial", "Terrain", "Bureau",
    name="property_type_enum", create_type=False
)
property_status_enum = postgresql.ENUM(
    "Disponible", "Réservé", "Vendu", "Loué", name="property_status_enum", create_type=False
)
property_vocation_enum = postgresql.ENUM(
    "Vente", "Location", name="property_vocation_enum", create_type=False
)
property_validation_enum = postgresql.ENUM(
    "Validée", "En attente", "Brouillon", name="property_validation_enum", create_type=False
)


def upgrade() -> None:
    # Create types explicitly
    op.execute("CREATE TYPE user_role_enum AS ENUM ('CHEF_AGENCE', 'AGENT', 'COORDINATEUR')")
    op.execute("CREATE TYPE zone_enum AS ENUM ('Tunis', 'La Marsa', 'Carthage', 'Gammarth', 'Sidi Bou Saïd', 'La Goulette', 'Le Bardo', 'Ariana', 'Ben Arous', 'Manouba')")
    op.execute("CREATE TYPE property_type_enum AS ENUM ('Appartement', 'Villa', 'Studio', 'Local commercial', 'Terrain', 'Bureau')")
    op.execute("CREATE TYPE property_status_enum AS ENUM ('Disponible', 'Réservé', 'Vendu', 'Loué')")
    op.execute("CREATE TYPE property_vocation_enum AS ENUM ('Vente', 'Location')")
    op.execute("CREATE TYPE property_validation_enum AS ENUM ('Validée', 'En attente', 'Brouillon')")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nom", sa.String(120), nullable=False),
        sa.Column("prenom", sa.String(120), nullable=False),
        sa.Column("telephone", sa.String(40), nullable=True),
        sa.Column("zone", zone_enum, nullable=True),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_zone", "users", ["zone"])

    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reference", sa.String(32), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("type", property_type_enum, nullable=False),
        sa.Column("status", property_status_enum, nullable=False),
        sa.Column("vocation", property_vocation_enum, nullable=False),
        sa.Column("validation", property_validation_enum, nullable=False),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="TND"),
        sa.Column("surface", sa.Float(), nullable=True),
        sa.Column("rooms", sa.Integer(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("floor", sa.Integer(), nullable=True),
        sa.Column("furnished", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("neighborhood", sa.String(120), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("owner_name", sa.String(255), nullable=True),
        sa.Column("owner_phone", sa.String(40), nullable=True),
        sa.Column("owner_email", sa.String(255), nullable=True),
        sa.Column(
            "responsible_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_properties_reference", "properties", ["reference"])
    op.create_index("ix_properties_city", "properties", ["city"])
    op.create_index("ix_properties_price", "properties", ["price"])
    op.create_index("ix_properties_type", "properties", ["type"])
    op.create_index("ix_properties_vocation", "properties", ["vocation"])
    op.create_index("ix_properties_status", "properties", ["status"])
    op.create_index("ix_properties_responsible", "properties", ["responsible_id"])

    op.create_table(
        "property_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "property_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_property_images_property_id", "property_images", ["property_id"])


def downgrade() -> None:
    op.drop_index("ix_property_images_property_id", table_name="property_images")
    op.drop_table("property_images")

    for ix in (
        "ix_properties_responsible",
        "ix_properties_status",
        "ix_properties_vocation",
        "ix_properties_type",
        "ix_properties_price",
        "ix_properties_city",
        "ix_properties_reference",
    ):
        op.drop_index(ix, table_name="properties")
    op.drop_table("properties")

    op.drop_index("ix_users_zone", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    property_validation_enum.drop(bind, checkfirst=True)
    property_vocation_enum.drop(bind, checkfirst=True)
    property_status_enum.drop(bind, checkfirst=True)
    property_type_enum.drop(bind, checkfirst=True)
    zone_enum.drop(bind, checkfirst=True)
    user_role_enum.drop(bind, checkfirst=True)
