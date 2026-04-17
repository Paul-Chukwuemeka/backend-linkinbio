from typing import TYPE_CHECKING

from lib.database import Base
from sqlalchemy import String, UUID, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from models.collection_model import Collection
from models.link_model import Link


if TYPE_CHECKING:
    from models.user_model import User

DEFAULT_STYLE = {
    "card_bg": "ffffff",
    "bg_type": "solid",
    "text_color": "000000",
    "button_radius": "round",
    "button_bg": "ffffff",
    "button_color": "000000",
    "button_type": "solid",
    "profile_image": None,
    "shadow": None,
    "font_style": "inter",
    "gradient": [],
    "title_size": "medium",
    "text_size": "medium",
    "gradient_type": "linear",
    "title_color": None,
}

class Card(Base):
    __tablename__ = 'cards'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, default="Untitled")
    user: Mapped["User"] = relationship("User", back_populates="cards")
    bio: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    style: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=DEFAULT_STYLE)
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
