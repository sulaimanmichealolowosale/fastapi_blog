from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, server_default="regular")
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))


class CommentReply(Base):
    __tablename__ = "comment_replies"
    id = Column(Integer, primary_key=True, nullable=False)
    body = Column(String, nullable=False)
    comment_id = Column(Integer, ForeignKey(
        "comments.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    approved = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner = relationship("User")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), nullable=False)

    body = Column(String, nullable=False)
    reply = Column(Boolean, nullable=False, server_default=text("0"))
    comment_id = Column(Integer, nullable=True)
    approved = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner = relationship("User")
    replies = relationship("CommentReply")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    category_id = Column(Integer, ForeignKey(
        "categories.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default=text("0"))
    image_url = Column(String, nullable=False)
    likes = Column(Integer, nullable=False, server_default=text('0'))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner = relationship("User")
    comments = relationship("Comment")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    posts = relationship("Post")
    owner = relationship("User")


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    owner = relationship("User")


class TagOnPost(Base):
    __tablename__ = "tags_on_posts"
    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), nullable=False)
    tag_title = Column(String, ForeignKey(
        "tags.title", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    posts = relationship("Post")
