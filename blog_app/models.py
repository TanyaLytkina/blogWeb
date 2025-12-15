from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    login: str
    password: str

    @validator('login')
    def login_must_be_simple(cls, v):
        if ' ' in v:
            raise ValueError('Login cannot contain spaces')
        return v


class PostCreate(BaseModel):
    authorId: int
    title: str
    content: str


class User(BaseModel):
    id: int
    email: str
    login: str
    password: str
    role: str = "user"
    createdAt: datetime = Field(alias="created_at", default_factory=datetime.now)
    updatedAt: datetime = Field(alias="updated_at", default_factory=datetime.now)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class Post(BaseModel):
    id: int
    authorId: int = Field(alias="author_id")
    title: str
    content: str
    createdAt: datetime = Field(alias="created_at", default_factory=datetime.now)
    updatedAt: datetime = Field(alias="updated_at", default_factory=datetime.now)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }