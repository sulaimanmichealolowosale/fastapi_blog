from unicodedata import category
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, oauth2

router = APIRouter(
    tags=["Category"],
    prefix="/categories"
)


@router.post("/", response_model=schemas.GetCategory)
def add_category(category: schemas.AddCategory, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_admin_user)):

    existing_category = db.query(models.Category).filter(
        models.Category.name == category.name).first()

    if existing_category != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the name: {category.name} already exist ")

    new_category = models.Category(owner_id=current_user.id, **category.dict())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/", response_model=List[schemas.GetCategory])
def get_categories(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    category = db.query(models.Category).all()
    return category


@router.get("/{category_id}", response_model=schemas.PostsByCategory)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    category = db.query(models.Category).join(models.Post, models.Category.id == models.Post.category_id,
                                              isouter=True).filter(models.Category.id == category_id).group_by(models.Category.id).first()
    if category == None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the id: {category_id} already exist ")
    return category


@router.put("/{category_id}", response_model=schemas.GetCategory)
def update_category(category_id: int, update_category: schemas.AddCategory, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_admin_user)):

    category_query = db.query(models.Category).filter(
        models.Category.id == category_id)
    category = category_query.first()

    if category == None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the id: {category_id} already exist ")
    if category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the requested action")

    category_query.update(update_category.dict(), synchronize_session=False)
    db.commit()
    return category_query.first()
