from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas, oauth2

router = APIRouter(tags=["Posts"], prefix="/posts")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.GetPost)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_admin_user)):
    existing_post = db.query(models.Post).filter(
        models.Post.title == post.title).first()

    if existing_post is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A post with the title: {post.title} already exist ")

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=list[schemas.GetPost])
def get_post(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10,
             skip: int = 0,
             search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(
        search)).limit(limit).offset(skip).all()

    return posts


@router.get("/{id}", response_model=schemas.PostWithComment)
def get_single_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).join(models.Comment, models.Post.id == models.Comment.post_id).filter(
        models.Post.id == id, models.Post.published == "True").group_by(models.Post.id).first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} does not exists")

    return post


@router.put("/{id}", response_model=schemas.GetPost, status_code=status.HTTP_201_CREATED)
def update_post(updated_post: schemas.CreatePost, id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_admin_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} does not exists")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} does not exists")

    if post.owner_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
