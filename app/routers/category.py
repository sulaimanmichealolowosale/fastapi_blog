from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, oauth2, utils
from app.schemas.category import *

router = APIRouter(
    tags=["Categories"],
    prefix="/categories"
)


@router.post("/", response_model=GetCategory)
def manage_categories(category: AddCategory, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):

    existing_category = db.query(models.Category).filter(
        models.Category.title == category.title).first()

    if existing_category is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the name: {category.title} already exist ")

    new_category = models.Category(
        owner_id=current_user.id, **category.dict())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/", response_model=List[GetCategory])
def manage_categories(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    categories = db.query(models.Category).all()
    return categories


@router.get("/category-id={id}", response_model=PostsByCategory)
def manage_categories(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    category = db.query(models.Category).join(models.Post, models.Category.id == models.Post.category_id,
                                              isouter=True).filter(models.Category.id == id).group_by(models.Category.id).first()
    utils.check_if_found(category, id, name="category")
    return category


@router.put("/category-id={id}", response_model=GetCategory)
def manage_categories(id: int, category: AddCategory, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_admin_user)):

    category_query = db.query(models.Category).filter(models.Category.id == id)
    category_result = category_query.first()

    existing_category = db.query(models.Category).filter(
        models.Category.title == category.title).first()

    if existing_category and id is not existing_category.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the title: {category.title} already exist")

    utils.check_if_found(category_result, id, name="category")
    utils.check_if_authorized(current_user.id, category_result.owner_id)
    

    category_query.update(category.dict(), synchronize_session=False)
    db.commit()
    return category_query.first()


@router.delete("/category-id={id}")
def manage_categories(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    category_query = db.query(models.Category).filter(models.Category.id == id)
    category_result = category_query.first()

    utils.check_if_found(category_result, id, name="category")

    utils.check_if_authorized(current_user.id, category_result.owner_id)
    
    category_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
