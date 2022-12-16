from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, oauth2
from app.database import get_db

router = APIRouter(
    tags=["Comment"]
)


@router.get("/comments")
def get_comments(current_user: int = Depends(oauth2.get_current_admin_user), db: Session = Depends(get_db)):
    comments = db.query(models.Comment).all()
    return comments


@router.post("/post-comment/{post_id}", response_model=schemas.GetComment)
def post_comment(post_id: int, comment: schemas.Comment, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    existing_post = db.query(models.Post).filter(
        models.Post.id == post_id).first()

    if existing_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} does not exists ")

    new_comment = models.Comment(
        user_id=current_user.id, post_id=post_id, **comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.put("/update-comment/{comment_id}")
def update_comment(comment_id: int, update_comment: schemas.Comment, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(
        models.Comment.id == comment_id)
    comment = comment_query.first()

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id: {comment_id} does not exist")

    if comment.user_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the requested action")

    comment_query.update(update_comment.dict(), synchronize_session=False)
    db.commit()
    return comment_query.first()


@router.put("/approve-comment/{comment_id}")
def update_comment_status(comment_id: int, update_comment: schemas.CommentStatus, db: Session = Depends(get_db),
                          current_user: int = Depends(oauth2.get_current_admin_user)):
    comment_query = db.query(models.Comment).filter(
        models.Comment.id == comment_id)
    existing_comment = comment_query.first()

    if existing_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id: {comment_id} does not exists ")

    comment_query.update(update_comment.dict(), synchronize_session=False)
    db.commit()
    return comment_query.first()


@router.delete("/delete-comment/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(
        models.Comment.id == comment_id)
    comment = comment_query.first()

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id: {comment_id} does not exists ")
                            
    if current_user.id is not comment.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")
    comment_query.delete(synchronize_session=False)
    db.commit()
    return {"Message": "Comment deleted", "status": status.HTTP_204_NO_CONTENT}
