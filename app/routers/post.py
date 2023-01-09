from fastapi import APIRouter, Depends, status, HTTPException, Response, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, oauth2, utils
from app.schemas.post import *
import shutil

router = APIRouter(tags=["Posts"], prefix="/posts")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetPost)
def manage_posts(post: CreatePost = Depends(), file: UploadFile = File(...), db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_admin_user)):
    existing_post = db.query(models.Post).filter(
        models.Post.title == post.title).first()

    category = db.query(models.Category).filter(
        models.Category.id == post.category_id).first()

    utils.check_if_found(category, id, name="category")

    if existing_post is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A post with the title: {post.title} already exist ")

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"the file: {file.filename} is not an image file")

    with open("media/"+file.filename, "wb") as image:
        shutil.copyfileobj(file.file, image)
    image_url = "media/"+file.filename

    new_post = models.Post(owner_id=current_user.id,
                           image_url=image_url, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=list[GetPost])
def manage_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10,
                 skip: int = 0, search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(
        search)).limit(limit).offset(skip).all()

    return posts


@router.get("/post-id={id}", response_model=GetCommentByPost)
def manage_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).join(models.Comment, models.Comment.post_id == models.Post.id,
                                      isouter=True).filter(models.Post.id == id, models.Post.published == True).group_by(models.Post.id).first()

    utils.check_if_found(post, id, name="post")
    return post


@router.put("/post-id={id}", response_model=GetPost, status_code=status.HTTP_201_CREATED)
def manage_posts(id: int, post: UpdatePost = Depends(), file: UploadFile = File(...), db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_admin_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post_result = post_query.first()

    existing_post = db.query(models.Post).filter(
        models.Post.title == post.title).first()

    category = db.query(models.Category).filter(
        models.Category.id == post.category_id).first()

    if existing_post and id is not existing_post.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A post with the title: {post.title} already exist")

    utils.check_if_found(category, id, name="category")
    utils.check_if_found(post_result, id, name="post")

    if post_result.owner_id is not current_user.id and current_user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"the file: {file.filename} is not an image file")

    with open("media/"+file.filename, "wb") as image:
        shutil.copyfileobj(file.file, image)
    image_url = "media/"+file.filename
    post.image_url=image_url
    post_query.update(post.dict() ,synchronize_session=False)
    db.commit()
    return post_query.first()


@router.delete("/post-id={id}")
def manage_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    utils.check_if_found(post, id, name="post")

    if post.owner_id is not current_user.id and current_user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
