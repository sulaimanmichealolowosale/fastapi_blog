from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, utils, models, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.GetUser)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)

    user.password = hashed_password
    existing_user = db.query(models.User).filter(
        models.User.email == user.email or models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Either the username or the Email already exists")

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[schemas.GetUser])
def get_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    users = db.query(models.User).all()
    return users
    


@router.get("/{id}", response_model=schemas.GetUser, status_code=status.HTTP_302_FOUND)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} is not found ")
    return user
