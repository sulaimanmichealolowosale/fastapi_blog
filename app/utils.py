from passlib.context import CryptContext
from fastapi import HTTPException, status

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password):
    hashed_password = password_context.hash(password)
    return hashed_password


def verify(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


super_admin = "superadmin"
writer = "writer"


def verify_super_admin(user):
    if user.role != super_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform the requested action")


def check_if_found(data, id, name=""):
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A {name} with id: {id} was not found")

def check_if_authorized(user_id, data_id):
    if user_id is not data_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorised to perform the requested action")
