from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .user import GetUser
from .comment import GetComment


class PostBase(BaseModel):
    title: str
    body: str
    published: Optional[bool] = False
    category_id: int


class CreatePost(PostBase):
    pass


class GetPost(PostBase):
    id: int
    created_at: datetime
    likes: int
    owner: GetUser

    class Config:
        orm_mode = True


class GetCommentByPost(GetPost):
    comments: List[GetComment] = []
