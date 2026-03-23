from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import Integer, String, UUID, ForeignKey, UniqueConstraint
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.cardModel import Card
    from models.LinkModel import Link



class Collection(Base):
    __tablename__ = 'collections'
    __table_args__ = (
        UniqueConstraint("card_id", "title", name="uq_collections_card_title"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    links: Mapped[list["Link"]] = relationship(
        "Link", back_populates="collection", cascade="all, delete", passive_deletes=True
    )
    card: Mapped["Card"] = relationship("Card", back_populates="collections")
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False
    )
