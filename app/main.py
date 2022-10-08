from fastapi import FastAPI
from .routers import user, auth, post, comment, category


app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(category.router)


@app.get("/")
def root():
    return {"message": "hello world"}
