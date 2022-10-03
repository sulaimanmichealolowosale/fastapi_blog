from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, utils, models, oauth2
from app.database import get_db

router = APIRouter(
    tags=["Comment"],
    prefix="/comment"
)


@router.post("/{post_id}", response_model=schemas.GetComment)
def post_comment(post_id: int, comment: schemas.Comment, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    existing_post = db.query(models.Post).filter(
        models.Post.id == post_id).first()

    if existing_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} does not exists ")

    new_comment = models.Comment(
        username=current_user.username, post_id=post_id, ** comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.put("/{comment_id}")
def update_comment_status(comment_id: int, update_comment: schemas.CommentStatus, db: Session = Depends(get_db)):

    comment_query = db.query(models.Comment).filter(
        models.Comment.id == comment_id)
    existing_comment = comment_query.first()

    if existing_comment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id: {comment_id} does not exists ")

    comment_query.update(update_comment.dict(), synchronize_session=False)
    db.commit()
    return comment_query.first()
