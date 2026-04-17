from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import Integer, String, UUID, ForeignKey
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.card_model import Card
    from models.collection_model import Collection



class Link(Base):
    __tablename__ = 'links'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    card: Mapped["Card"] = relationship("Card", back_populates="links")
    collection: Mapped["Collection | None"] = relationship(
        "Collection", back_populates="links"
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False
    )
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=True,
    )
