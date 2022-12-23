from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app import models, oauth2, utils
from app.schemas.comment import *
from app.database import get_db

router = APIRouter(
    tags=["Comments"],
    prefix="/comments"
)


@router.get("/")
def manage_comments(current_user: int = Depends(oauth2.get_current_admin_user), db: Session = Depends(get_db)):
    comments = db.query(models.Comment).all()
    return comments


@router.get("/article-comments/article-id={id}")
def manage_comments(id: int, current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(
        models.Comment.post_id == id, models.Comment.approved == True).all()
        
    post = db.query(models.Post).filter(models.Post.id == id).first()
    utils.check_if_found(post, id, name="post")

    return comments


@router.get("/comment-replies/comment-id={id}", response_model=GetReplyByComment)
def manage_comments(id: int, current_user: int = Depends(oauth2.get_current_user),
                    db: Session = Depends(get_db)):
    replies = db.query(models.Comment).join(models.CommentReply, models.Comment.id == models.CommentReply.comment_id,
                                            isouter=True).filter(models.Comment.id == id, models.Comment.approved == True).group_by(models.Comment.id).first()

    utils.check_if_found(replies, id, name="comment")

    return replies


@router.post("/comment/article-id={id}", response_model=GetComment)
def manage_comments(id: int, comment: Comment, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    existing_post = db.query(models.Post).filter(
        models.Post.id == id).first()

    utils.check_if_found(existing_post, id, name="post")

    if existing_post.published is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot comment on an unpublished post")

    new_comment = models.Comment(
        user_id=current_user.id, post_id=id, **comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.post("/comment/comment-id={id}/post-id={post_id}", response_model=GetComment)
def manage_comments(id: int, post_id: int, comment: Comment,
                    current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):

    existing_comment = db.query(models.Comment).filter(
        models.Comment.id == id).first()

    existing_post = db.query(models.Post).filter(
        models.Post.id == post_id).first()

    utils.check_if_found(existing_comment, id, name="comment")

    utils.check_if_found(existing_post, id, name="post")

    if existing_post.published is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot comment on an unpublished post")

    new_comment = models.Comment(comment_id=id, post_id=post_id,
                                 reply=True, user_id=current_user.id, **comment.dict())
    db.add(new_comment)

    new_reply = models.CommentReply(
        comment_id=id, post_id=post_id, user_id=current_user.id, **comment.dict())
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)
    return new_reply


@router.put("/comment/comment-id={id}", response_model=GetComment)
def manage_comments(id: int, update_comment: Comment, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(
        models.Comment.id == id)
    comment_result = comment_query.first()

    utils.check_if_found(comment_result, id, name="comment")

    utils.check_if_authorized(current_user.id, comment_result.user_id)

    comment_query.update(update_comment.dict(), synchronize_session=False)
    db.commit()
    return comment_query.first()


@router.put("/approve-comment/comment-id={id}")
def manage_comments(id: int, update_comment: CommentStatus, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_admin_user)):

    comment_query = db.query(models.Comment).filter(
        models.Comment.id == id)
    existing_comment = comment_query.first()

    utils.check_if_found(existing_comment, id, name="comment")

    comment_query.update(update_comment.dict(), synchronize_session=False)
    db.commit()
    return comment_query.first()


@router.delete("/remove-comment/comment-id={id}")
def manage_comments(id: int, db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(
        models.Comment.id == id)
    comment_result = comment_query.first()

    utils.check_if_found(comment_result, id, name="comment")

    utils.check_if_authorized(current_user.id, comment_result.user_id)
    comment_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
