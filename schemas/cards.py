from pydantic import BaseModel, ConfigDict, Field
import uuid
from enum import Enum

from schemas.collections import CollectionPublic
from schemas.links import LinkPublic


class CardStyle(BaseModel):
    card_bg: str = "ffffff"
    bg_type: str = "solid"
    text_color: str = "000000"
    button_radius: str = "round"
    button_bg: str = "ffffff"
    button_color: str = "000000"
    button_type: str = "solid"
    profile_image: str | None = None
    shadow: str | None = None
    font_style: str = "inter"
    gradient: list[str] = Field(default_factory=list)
    title_size: str = "medium"
    text_size: str = "medium"
    gradient_type: str = "linear"
    title_color: str | None = None

class CardCreate(BaseModel):
    name: str | None = None


class CardUpdate(BaseModel):
    name: str | None = None
    
class CardStyleUpdate(BaseModel):
    style: CardStyle | None = None

class CardItemType(str, Enum):
    link = "link"
    collection = "collection"

class CardItemReorderItem(BaseModel):
    type: CardItemType
    id: uuid.UUID
    position: int = Field(ge=0)


class CardItemReorderRequest(BaseModel):
    items: list[CardItemReorderItem]

class CurrentCardUpdate(BaseModel):
    card_id: uuid.UUID


class CardPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    links: list[LinkPublic] = Field(default_factory=list)
    collections: list[CollectionPublic] = Field(default_factory=list)
    style: CardStyle
    

class CardItem(BaseModel):
    type: CardItemType
    position: int
    content: LinkPublic | CollectionPublic
    

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    username: str
    fullname: str
    bio: str | None = None
    avatar_url: str | None = None
    
    
class CardPublicList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    items_list: list[CardItem] = Field(default_factory=list)
    style: CardStyle
    user: UserPublic
    
    
    
