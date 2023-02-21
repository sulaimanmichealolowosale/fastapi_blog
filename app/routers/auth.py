from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, utils, oauth2
from app.schemas.auth import Token
from datetime import timedelta

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(response: Response, login_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == login_details.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(login_details.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    response.delete_cookie("refresh_token")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_access_token(
        data={"user_id": user.id}, expire_time=timedelta(days=1))
    response.set_cookie("refresh_token", refresh_token, httponly=True)
    response.set_cookie("access_token", access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", 'role': user.role, "email": user.email, "username": user.username}


@router.get("/refresh")
def refresh(response: Response, refresh_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    
    credentials_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                          detail=f"Could not validate credentials", headers={"www-authenticate": "bearer"})
    payload = oauth2.verify_access_token(
        refresh_token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == payload.id).first()
    
    access_token = oauth2.create_access_token(data={"user_id": payload.id})
    response.delete_cookie("access_token")
    response.set_cookie("access_token", access_token,  httponly=True)
    return {"access_token": access_token, "role": user.role, "username": user.username}


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out"}


