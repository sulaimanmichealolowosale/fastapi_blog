from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models, utils, oauth2


router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(login_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == login_details.username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(login_details.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id, "user_role":user.role})
    return {"access_token": access_token, "token_type": "bearer"}
