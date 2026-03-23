from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.CollectionModel import Collection
from models.LinkModel import Link

if TYPE_CHECKING:
    from models.userModel import User


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
        "Link",
        back_populates="card",
        cascade="all, delete-orphan",
        order_by=lambda: (Link.position.asc(), Link.id.asc()),
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        back_populates="card",
        cascade="all, delete-orphan",
        order_by=lambda: (Collection.position.asc(), Collection.id.asc()),
    )
