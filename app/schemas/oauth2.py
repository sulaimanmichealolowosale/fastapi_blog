from typing import Optional
from pydantic import BaseModel


class TokenData(BaseModel):
    id: Optional[int] = None
