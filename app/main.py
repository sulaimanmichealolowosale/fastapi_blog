from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, auth, post, comment, category, like, tag



origin = ['http://localhost:3000', 'http://127.0.0.1:3000',
          'https://localhost:3000', 'https://127.0.0.1:3000']
          
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class Route:
    def __init__(self, *args):
        [app.include_router(key.router) for key in args]


auth_route = Route(auth, user, post, category, tag, comment, like)


@app.get("/")
def root():
    return {"message": "hello world"}
