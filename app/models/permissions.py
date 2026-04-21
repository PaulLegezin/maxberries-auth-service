from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="roles_permissions", back_populates="permissions"
    )
