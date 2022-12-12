from fastapi import FastAPI
from .routers import user, auth, post, comment, category

app = FastAPI()


class Route:
    def __init__(self, *args):
        [app.include_router(key.router) for key in args]


auth_route = Route(auth, user, post, comment, category)


@app.get("/")
def root():
    return {"message": "hello world"}
