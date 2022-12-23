from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime
from .user import GetUser
from .post import GetPost

class CreateTag(BaseModel):
    title: constr(strict=True, strip_whitespace=True)


class GetTag(BaseModel):
    id: int
    title: str
    owner: GetUser

    class Config:
        orm_mode = True


class PostsByTag(GetTag):
    posts: List[GetPost] = []
