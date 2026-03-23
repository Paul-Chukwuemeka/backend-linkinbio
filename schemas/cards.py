from pydantic import BaseModel, ConfigDict, Field
import uuid

from schemas.collections import CollectionPublic
from schemas.links import LinkPublic


class CardCreate(BaseModel):
    name: str | None = None


class CardUpdate(BaseModel):
    name: str | None = None


class CardPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    links: list[LinkPublic] = Field(default_factory=list)
    collections: list[CollectionPublic] = Field(default_factory=list)
