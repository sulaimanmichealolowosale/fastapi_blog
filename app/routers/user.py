from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app import utils, models, oauth2
from app.schemas.user import *
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetUser)
def manage_users(user: CreateUser, db: Session = Depends(get_db)):
    hashed_password = utils.password_hash(user.password)

    user.password = hashed_password
    existing_user = db.query(models.User).filter(
        models.User.email == user.email or models.User.username == user.username).first()

    if existing_user is not None:
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
        users = db.query(models.User).filter(
            models.User.id == current_user.id).all()
        return users

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
