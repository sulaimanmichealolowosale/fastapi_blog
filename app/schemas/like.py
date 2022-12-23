from pydantic import BaseModel, conint


class Like(BaseModel):
    like: conint(gt=-1, lt=2)


class IncreaseLikes(BaseModel):
    likes: int
