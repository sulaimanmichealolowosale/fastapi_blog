from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import oauth2, models, utils
from app.schemas.like import *

router = APIRouter(tags=["Like"], prefix="/like")


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def like_post(post_id: int, like: Like, current_user: int = Depends(oauth2.get_current_user),
              db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post_result = post_query.first()

    like_query = db.query(models.Like).filter(
        models.Like.post_id == post_id, models.Like.user_id == current_user.id)
    found_like = like_query.first()

    utils.check_if_found(post_result, id, name="post")

    likes_count = IncreaseLikes
    likes_count.likes = post_result.likes

    if (like.like == 1):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'User with id: {current_user.id} already likes the post with id: {post_id}')
        new_like = models.Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        likes_count.likes += 1
        post_query.update(
            {models.Post.likes: likes_count.likes}, synchronize_session=False)
        db.commit()
        db.refresh(new_like)
        return {"message": "Post liked"}
    elif (like.like == 0):
        if found_like is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'User with id: {current_user.id} do not like the post with id: {post_id} yet')

        like_query.delete(synchronize_session=False)
        likes_count.likes -= 1
        post_query.update(
            {models.Post.likes: likes_count.likes}, synchronize_session=False)
        db.commit()

        return {"message": "Post disliked"}
