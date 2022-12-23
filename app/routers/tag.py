from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app import oauth2, models, utils
from app.schemas.tag import *
from app.database import get_db

router = APIRouter(tags=["Tags"], prefix="/tags")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetTag)
def manage_tags(tag: CreateTag, current_user: int = Depends(oauth2.get_current_admin_user),
                db: Session = Depends(get_db)):
    existing_tag = db.query(models.Tag).filter(
        models.Tag.title == tag.title).first()

    if existing_tag is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A tag with the title: {tag.title} already exists ")
    new_tag = models.Tag(user_id=current_user.id, **tag.dict())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/", response_model=list[GetTag])
def manage_tags(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    tags = db.query(models.Tag).all()
    return tags


@router.get("/tag-id={id}", response_model=GetTag)
def manage_tags(id, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    tag = db.query(models.Tag).filter(models.Tag.id == id).first()

    utils.check_if_found(tag, id, name="tag")
    return tag


@router.put("/tag-id={id}", response_model=GetTag, status_code=status.HTTP_201_CREATED)
def manage_tags(id: int, tag: CreateTag, current_user: int = Depends(oauth2.get_current_admin_user),
                db: Session = Depends(get_db)):

    tag_query = db.query(models.Tag).filter(models.Tag.id == id)
    tag_result = tag_query.first()

    existing_tag = db.query(models.Tag).filter(
        models.Tag.title == tag.title).first()

    if existing_tag and id is not existing_tag.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"A tag with the title: {tag.title} already exist")

    utils.check_if_found(tag_result, id, name="tag")

    tag_query.update(tag.dict(), synchronize_session=False)
    db.commit()
    return tag_query.first()


@router.post("/tag-to-article/article-id={id}", status_code=status.HTTP_201_CREATED)
def manage_tags(id: int, tag: CreateTag, current_user: int = Depends(oauth2.get_current_admin_user),
                db: Session = Depends(get_db)):

    existing_tag = db.query(models.Tag).filter(
        models.Tag.title == tag.title).first()

    existing_post = db.query(models.Post).filter(models.Post.id == id).first()

    utils.check_if_found(existing_post, id, name="post")

    if existing_tag is None:
        new_tag = models.Tag(user_id=current_user.id, **tag.dict())
        db.add(new_tag)
        db.commit()

    existing_tag_on_post = db.query(models.TagOnPost).filter(
        models.TagOnPost.tag_title == tag.title, models.TagOnPost.post_id == id).first()

    if existing_tag_on_post is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The post with id: {id} already has the tag with title: {tag.title}")

    new_tag_on_post = models.TagOnPost(post_id=id, tag_title=tag.title)
    db.add(new_tag_on_post)
    db.commit()
    db.refresh(new_tag_on_post)
    return new_tag_on_post


@router.delete("/remove-from-post/article-id={id}")
def manage_tags(tag_title: str, id: int, current_user: int = Depends(oauth2.get_current_admin_user),
                db: Session = Depends(get_db)):
                
    tag_query = db.query(models.TagOnPost).filter(
        models.TagOnPost.tag_title == tag_title, models.TagOnPost.post_id == id)
    tag_result = tag_query.first()

    if tag_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} does not have the tag with the title: {tag_title}")

    tag_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/tag-id={id}")
def manage_tags(id: int, current_user: int = Depends(oauth2.get_current_admin_user), db: Session = Depends(get_db)):
    tag_query = db.query(models.Tag).filter(models.Tag.id == id)
    tag_result = tag_query.first()

    utils.check_if_found(tag_result, id, name="tag")
    
    tag_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
