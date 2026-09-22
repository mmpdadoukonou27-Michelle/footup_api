from pydantic import BaseModel
from typing import Optional

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    club: Optional[str] = None
    position: Optional[str] = None
    region: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class PushTokenUpdate(BaseModel):
    push_token: str