from pydantic import BaseModel, EmailStr


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    username:str
    email:EmailStr
    role:str
    access_token: str
    token_type: str
