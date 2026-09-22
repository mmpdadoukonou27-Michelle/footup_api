from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from services.match_service import create_match, join_match, update_score, finish_match
from services.push_service import send_push

router = APIRouter()

@router.post("/match/invite/{friend_id}")
async def invite_friend(friend_id: int, cu: dict = Depends(get_current_user)):
    """Invite un ami à un match 1v1."""
    match = await create_match(cu["id"], friend_id)
    if not match:
        raise HTTPException(500, "Erreur création match")
    
    # Envoyer une notif à l'ami
    await send_push(friend_id, "⚔️ Défi reçu !", 
                   f"{cu.get('name')} te défie en 1v1 !", 
                   {"type": "match_invite", "match_id": match["id"], "from_user_id": cu["id"]})
    
    return {"match_id": match["id"], "status": "waiting"}

@router.post("/match/{match_id}/join")
async def join_match_route(match_id: str, cu: dict = Depends(get_current_user)):
    """Rejoint un match."""
    result = await join_match(match_id, cu["id"])
    if not result:
        raise HTTPException(404, "Match introuvable")
    return {"status": "active"}

@router.post("/match/{match_id}/score")
async def update_match_score(match_id: str, body: dict, cu: dict = Depends(get_current_user)):
    """Met à jour le score."""
    result = await update_score(match_id, cu["id"], body.get("score", 0), body.get("data", {}))
    if not result:
        raise HTTPException(400, "Erreur mise à jour score")
    return {"status": "ok"}

@router.post("/match/{match_id}/finish")
async def finish_match_route(match_id: str, body: dict, cu: dict = Depends(get_current_user)):
    """Termine le match."""
    await finish_match(match_id, body.get("winner_id"))
    return {"status": "finished"}