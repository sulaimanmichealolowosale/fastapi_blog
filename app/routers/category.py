from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, oauth2

router = APIRouter(
    tags=["Category"],
    prefix="/categories"
)


@router.get("/", response_model=List[schemas.GetCategory])
def fetch_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    categories = db.query(models.Category).all()
    return categories


@router.get("/{id}", response_model=schemas.PostsByCategory)
def fetch_single(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    category = db.query(models.Category).join(models.Post, models.Category.id == models.Post.category_id,
                                              isouter=True).filter(models.Category.id == id).group_by(models.Category.id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A category with the id: {id} does not exist ")
    return category


@router.post("/", response_model=schemas.GetCategory)
def add_new(category: schemas.AddCategory, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):

    existing_category = db.query(models.Category).filter(
        models.Category.title == category.title).first()

    if existing_category is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the name: {category.name} already exist ")

    new_category = models.Category(
        owner_id=current_user.id, **category.dict())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{id}", response_model=schemas.GetCategory)
def update_category(id: int, category: schemas.AddCategory, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_admin_user)):

    category_query = db.query(models.Category).filter(models.Category.id == id)
    category_result = category_query.first()

    if category_result is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the id: {id} already exist ")
    if category_result.owner_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the categoryed action")

    category_query.update(category.dict(), synchronize_session=False)
    db.commit()
    return category_query.first()


@router.delete("/{id}")
def delete_category(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    category_query = db.query(models.Category).filter(models.Category.id == id)
    category_rersult = category_query.first()

    if category_rersult is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A category with the id: {id} does not exist ")
    if category_rersult.owner_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the categoryed action")
    category_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

