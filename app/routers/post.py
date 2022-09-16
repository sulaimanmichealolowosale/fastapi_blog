from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, oauth2


router = APIRouter(tags=["Posts"], prefix="/posts")


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(db: Session = Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):
    pass
