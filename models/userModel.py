from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

if TYPE_CHECKING:
    from models.cardModel import Card


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    avatar_url: Mapped[str | None] = mapped_column(
        String(2048), nullable=True, default=None
    )
    theme: Mapped[str] = mapped_column(
        String(50), nullable=False, default="default", server_default="default"
    )
    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="user", cascade="all, delete-orphan"
    )
