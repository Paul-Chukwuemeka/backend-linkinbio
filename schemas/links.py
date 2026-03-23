from pydantic import BaseModel, ConfigDict, Field
import uuid


class LinkCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=2048)
    card_id: uuid.UUID
    collection_id: uuid.UUID | None = None


class LinkUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, min_length=1, max_length=2048)
    collection_id: uuid.UUID | None = None


class LinkMove(BaseModel):
    collection_id: uuid.UUID | None = None


class LinkReorderItem(BaseModel):
    id: uuid.UUID
    position: int = Field(ge=0)


class LinkReorderRequest(BaseModel):
    card_id: uuid.UUID
    collection_id: uuid.UUID | None = None
    items: list[LinkReorderItem]


class LinkPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    card_id: uuid.UUID
    collection_id: uuid.UUID | None
    position: int
