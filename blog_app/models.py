from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator

class User(BaseModel):
    id: int
    email: str
    login: str
    password: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v

class Post(BaseModel):
    id: int
    authorId: int
    title: str
    content: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()

class UserCreate(BaseModel):
    email: str
    login: str
    password: str

class PostCreate(BaseModel):
    authorId: int
    title: str
    content: str

class UserResponse(User):
    pass

class PostResponse(Post):
    pass