from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class PostBase(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True


class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Optional[str] = "regular"


class GetUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class CreatePost(PostBase):
    pass


class Comment(BaseModel):
    body: str


class CommentStatus(BaseModel):
    approved: bool


class GetPost(PostBase):
    id: int
    created_at: datetime
    owner: GetUser

    class Config:
        orm_mode = True


class GetComment(BaseModel):
    id: int
    body: str
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


# class PostWithComment(BaseModel):
#     post:GetPost
