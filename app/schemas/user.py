from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    email: EmailStr
    username: constr(strip_whitespace=True, strict=True,
                     min_length=4, max_length=20)
    password: constr(strip_whitespace=True, strict=True,
                     min_length=8, max_length=20)
    role: Optional[str] = "regular"


class GetUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True
