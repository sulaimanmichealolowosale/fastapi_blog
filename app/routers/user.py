from fastapi import APIRouter, status, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from app import utils, models, oauth2
from app.schemas.user import *
from app.database import get_db
from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetUser)
def manage_users(user: CreateUser, db: Session = Depends(get_db)):
    hashed_password = utils.password_hash(user.password)

    user.password = hashed_password
    existing_email = db.query(models.User).filter(
        models.User.email == user.email).first()

    existing_username = db.query(models.User).filter(
        models.User.username == user.username).first()

    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="The Email already exists")
    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Either the username or the Email already exists")

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[GetUser])
def manage_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):

    if current_user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the requested action")

    users = db.query(models.User).all()
    return users


@router.get("/user-id={id}", response_model=GetUser, status_code=status.HTTP_302_FOUND)
def manage_users(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    utils.check_if_found(user, id, name="User")
    utils.verify_super_admin(current_user)

    return user


@router.delete("/user-id={id}")
def manage_users(id: int, current_user: int = Depends(oauth2.get_current_admin_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user_result = user_query.first()

    utils.check_if_found(user_result, id, name="User")

    utils.verify_super_admin(current_user)
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
