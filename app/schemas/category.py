from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .user import GetUser
from .post import GetPost

class CategoryBase(BaseModel):
    title: str
    description: Optional[str] = ""


class AddCategory(CategoryBase):
    pass


class GetCategory(CategoryBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: GetUser

    class Config:
        orm_mode = True


class PostsByCategory(GetCategory):
    posts: List[GetPost] = []
