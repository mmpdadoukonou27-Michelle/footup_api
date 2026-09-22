from fastapi import APIRouter, HTTPException, Depends
from models.message import MessageSend
from dependencies import get_current_user
from services import message_service
from models.message import SessionShare

router = APIRouter()

@router.get("/messages/unread-count")
async def unread_count(cu: dict = Depends(get_current_user)):
    return await message_service.get_unread_count(cu["id"])

@router.get("/messages/conversations")
async def get_conversations(cu: dict = Depends(get_current_user)):
    return await message_service.get_conversations(cu["id"])

@router.get("/messages/{friend_id}")
async def get_messages(friend_id: int, cu: dict = Depends(get_current_user)):
    return await message_service.get_messages(cu["id"], friend_id)

@router.get("/messages/{friend_id}/status")
async def get_conversation_status(friend_id: int, cu: dict = Depends(get_current_user)):
    """NOUVEAU : Récupère le statut de conversation (ami + demande en attente)."""
    try:
        return await message_service.get_conversation_status(cu["id"], friend_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{friend_id}")
async def send_message(friend_id: int, body: MessageSend, cu: dict = Depends(get_current_user)):
    if not body.content.strip():
        raise HTTPException(400, "Message vide")
    try:
        result = await message_service.send_message(cu["id"], friend_id, body.content.strip(), cu.get("name", "Coéquipier"))
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/messages/{friend_id}/read")
async def mark_read(friend_id: int, cu: dict = Depends(get_current_user)):
    return await message_service.mark_read(cu["id"], friend_id)

# ─── NOUVEAUX ENDPOINTS POUR LES DEMANDES DE CONVERSATION ───

@router.get("/conversation-requests")
async def get_conversation_requests(cu: dict = Depends(get_current_user)):
    """Récupère les demandes de conversation reçues."""
    try:
        return await message_service.get_conversation_requests(cu["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation-requests/{request_id}/accept")
async def accept_conversation_request(request_id: str, cu: dict = Depends(get_current_user)):
    """Accepte une demande de conversation."""
    try:
        return await message_service.accept_conversation_request(request_id, cu["id"], cu.get("name", "Quelquun"))
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/conversation-requests/{request_id}/decline")
async def decline_conversation_request(request_id: str, cu: dict = Depends(get_current_user)):
    """Refuse une demande de conversation."""
    try:
        return await message_service.decline_conversation_request(request_id, cu["id"])
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/messages/{friend_id}/share-session")
async def share_session_route(friend_id: int, body: SessionShare, cu: dict = Depends(get_current_user)):
    """Partage une session de jeu dans le chat."""
    try:
        result = await message_service.share_session(
            cu["id"], 
            friend_id, 
            body.session_id, 
            body.message, 
            cu.get("name", "Coéquipier")
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))