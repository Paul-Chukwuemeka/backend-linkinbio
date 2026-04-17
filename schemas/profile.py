from pydantic import BaseModel, ConfigDict, Field
import uuid

from schemas.cards import CardPublic


class UserProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    fullname: str
    bio: str | None = None
    avatar_url: str | None = None
    theme: str
    current_card: uuid.UUID
    



class UserProfilePublic(UserProfileBase):
    cards: list[CardPublic] = Field(default_factory=list)


class CurrentUserProfile(UserProfileBase):
    email: str
    cards: list[CardPublic] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    fullname: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=2048)
    theme: str | None = Field(default=None, max_length=50)
