from pydantic import BaseModel
from typing import Optional

class MessageSend(BaseModel):
    content: str

class ConversationRequestResponse(BaseModel):
    type: str = "conversation_request"
    status: str
    message: str

class SessionShare(BaseModel):
    session_id: str
    message: Optional[str] = None
    