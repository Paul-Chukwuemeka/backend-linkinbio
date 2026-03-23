from pydantic import BaseModel, ConfigDict, Field
import uuid


class CollectionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    card_id: uuid.UUID
    position: int


class CollectionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    card_id: uuid.UUID


class CollectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)


class CollectionReorderItem(BaseModel):
    id: uuid.UUID
    position: int = Field(ge=0)


class CollectionReorderRequest(BaseModel):
    card_id: uuid.UUID
    items: list[CollectionReorderItem]
