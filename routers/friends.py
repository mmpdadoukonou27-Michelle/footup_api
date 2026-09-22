from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from services import friend_service
from database.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/friends")
async def get_friends(cu: dict = Depends(get_current_user)):
    return await friend_service.get_friends(cu["id"])

@router.get("/friends/requests")
async def get_friend_requests(cu: dict = Depends(get_current_user)):
    return await friend_service.get_friend_requests(cu["id"])

@router.post("/friends/request/{target_user_id}")
async def send_friend_request(target_user_id: int, cu: dict = Depends(get_current_user)):
    if cu["id"] == target_user_id:
        raise HTTPException(400, "Tu ne peux pas t'ajouter toi-même.")
    try:
        return await friend_service.send_request(cu["id"], target_user_id, cu.get("name", "Quelquun"))
    except Exception as e:
        raise HTTPException(400, str(e))

@router.put("/friends/request/{request_id}/accept")
async def accept_friend_request(request_id: int, cu: dict = Depends(get_current_user)):
    try:
        return await friend_service.accept_request(request_id, cu["id"], cu.get("name", "Quelquun"))
    except Exception as e:
        raise HTTPException(404, str(e))

@router.put("/friends/request/{request_id}/decline")
async def decline_friend_request(request_id: int, cu: dict = Depends(get_current_user)):
    return await friend_service.decline_request(request_id, cu["id"])

@router.delete("/friends/{friend_id}")
async def remove_friend(friend_id: int, cu: dict = Depends(get_current_user)):
    return await friend_service.remove_friend(cu["id"], friend_id)

@router.get("/users/search")
async def search_users(q: str = "", cu: dict = Depends(get_current_user)):
    return await friend_service.search_users(q, cu["id"])

@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int, cu: dict = Depends(get_current_user)):
    # 1. Infos utilisateur
    res = supabase.table("users").select("id,name,avatar_url,club,position,region,bio,age,xp").eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(404, "Joueur introuvable")
    user = res.data[0]

    # 2. Stats réelles - avec les VRAIS noms de colonnes
    sessions = supabase.table("sessions").select(
        "score, avg_force_g, max_force_g, total_hits, avg_reaction_ms, duration_s, avg_speed_kmh, total_shots, total_score, avg_force_n, xp_gained, combo_max"
    ).eq("user_id", user_id).execute().data or []

    n = len(sessions)

    # Vitesse estimée depuis le temps de réaction moyen
    def reaction_to_speed(reaction_ms: float) -> float:
        if reaction_ms <= 0:
            return 0.0
        speed = max(10.0, 90.0 - (reaction_ms - 200) * 0.09)
        return round(min(speed, 120.0), 1)

    avg_reaction_ms = round(
        sum(s.get("avg_reaction_ms") or 0 for s in sessions) / max(n, 1), 0
    ) if sessions else 0

    # Calcul des stats avec les bons noms de colonnes
    total_score = sum(s.get("total_score") or s.get("score") or 0 for s in sessions)
    total_shots = sum(s.get("total_shots") or s.get("total_hits") or 0 for s in sessions)
    avg_power = round(sum(s.get("avg_force_g") or s.get("avg_force_n") or 0 for s in sessions) / max(n, 1), 1) if sessions else 0
    max_power = round(max((s.get("max_force_g") or s.get("max_force_n") or 0 for s in sessions), default=0), 1)
    
    # Vitesse : soit avg_speed_kmh direct, soit calculée depuis réaction
    avg_speed = 0
    if sessions:
        direct_speed = sum(s.get("avg_speed_kmh") or 0 for s in sessions) / max(n, 1)
        if direct_speed > 0:
            avg_speed = round(direct_speed, 1)
        else:
            avg_speed = reaction_to_speed(avg_reaction_ms)

    stats = {
        "total_sessions": n,
        "total_score": total_score if total_score > 0 else user.get("xp", 0),
        "total_shots": total_shots,
        "avg_power": avg_power,
        "max_power": max_power,
        "avg_speed": avg_speed,
        "avg_reaction": int(avg_reaction_ms),
    }

    # 3. Statut d'amitié
    friend_status = await friend_service.get_friend_status(cu["id"], user_id)

    return {
        "user": user,
        "stats": stats,
        "friend_status": friend_status,
    }