from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password):
    hashed_password = password_context.hash(password)
    return hashed_password


def verify(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)
