from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    email: EmailStr
    username: constr(strip_whitespace=True, strict=True,
                     min_length=4, max_length=20)
    password: str
    role: Optional[str] = "regular"


class GetUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
