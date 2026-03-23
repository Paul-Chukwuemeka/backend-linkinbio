from enum import Enum
import uuid

from pydantic import BaseModel, Field

from schemas.collections import CollectionPublic
from schemas.links import LinkPublic


class CardItemType(str, Enum):
    link = "link"
    collection = "collection"


class CardItem(BaseModel):
    type: CardItemType
    position: int
    link: LinkPublic | None = None
    collection: CollectionPublic | None = None


class CardItemReorderItem(BaseModel):
    type: CardItemType
    id: uuid.UUID
    position: int = Field(ge=0)


class CardItemReorderRequest(BaseModel):
    items: list[CardItemReorderItem]
