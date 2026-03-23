from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

if TYPE_CHECKING:
    from models.userModel import User
    from models.LinkModel import Link
    from models.CollectionModel import Collection


class Card(Base):
    __tablename__ = 'cards'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, default="Untitled")
    user: Mapped["User"] = relationship("User", back_populates="cards")
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    links: Mapped[list["Link"]] = relationship(
        "Link", back_populates="card", cascade="all, delete-orphan"
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection", back_populates="card", cascade="all, delete-orphan"
    )
