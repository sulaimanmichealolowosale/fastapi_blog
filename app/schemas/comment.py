from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime
from .user import GetUser

class Comment(BaseModel):
    body: constr(strip_whitespace=True)


class CommentStatus(BaseModel):
    approved: bool


class GetComment(BaseModel):
    id: int
    body: str
    user_id: int
    approved: bool
    created_at: datetime
    owner: GetUser

    class Config:
        orm_mode = True




class GetReplyByComment(GetComment):
    replies: List[GetComment] = []
