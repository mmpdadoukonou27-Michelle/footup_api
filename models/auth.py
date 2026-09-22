from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    role: Optional[str] = "player"

class UserLogin(BaseModel):
    email: str
    password: str