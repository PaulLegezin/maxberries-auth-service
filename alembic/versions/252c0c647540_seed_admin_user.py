import uuid
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from app.core.security import get_pwd_hash

# revision identifiers, used by Alembic.
revision: str = "252c0c647540"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "roles_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.execute(
        "INSERT INTO roles (name, description) VALUES "
        "('admin', 'Суперюзер') ON CONFLICT DO NOTHING"
    )

    permissions_to_add = [
        ("user.access", "Доступ к работе с пользователями"),
        ("role.access", "Доступ к работе с ролями"),
        ("permission.access", "Доступ к работе с разрешениями"),
    ]

    for code, desc in permissions_to_add:
        op.execute(
            sa.text(
                "INSERT INTO permissions (code, description) "
                "VALUES (:code, :desc) ON CONFLICT DO NOTHING"
            ).bindparams(code=code, desc=desc)
        )

    connection = op.get_bind()
    admin_role_id = connection.execute(
        sa.text("SELECT id FROM roles WHERE name = 'admin'")
    ).scalar()

    perm_ids = connection.execute(
        sa.text(
            "SELECT id FROM permissions WHERE code IN "
            "('user.access', 'role.access', 'permission.access')"
        )
    ).fetchall()

    for row in perm_ids:
        op.execute(
            sa.text(
                "INSERT INTO roles_permissions (role_id, permission_id) "
                "VALUES (:r_id, :p_id) ON CONFLICT DO NOTHING"
            ).bindparams(r_id=admin_role_id, p_id=row[0])
        )

    password_hash = get_pwd_hash("admin_password_123")
    op.execute(
        sa.text(
            "INSERT INTO users (id, email, name, password_hash, role_id) "
            "VALUES (:id, :email, :name, :hash, :role_id) "
            "ON CONFLICT (email) DO NOTHING"
        ).bindparams(
            id=uuid.uuid4(),
            email="admin@example.com",
            name="Administrator",
            hash=password_hash,
            role_id=admin_role_id,
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
