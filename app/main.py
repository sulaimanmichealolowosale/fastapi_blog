from fastapi import FastAPI
from .routers import user, auth, post, comment


app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)


@app.get("/")
def root():
    return {"message": "hello world"}
