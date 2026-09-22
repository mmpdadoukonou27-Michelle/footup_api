from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from services.stats_service import get_user_stats
from database.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/sessions/stats")
async def get_stats(cu: dict = Depends(get_current_user)):
    return await get_user_stats(cu["id"])

@router.get("/sessions")
async def get_sessions(cu: dict = Depends(get_current_user)):
    """Récupère l'historique des sessions d'un utilisateur."""
    try:
        sessions = supabase.table("sessions").select("*").eq("user_id", cu["id"]).order("created_at", desc=True).limit(50).execute()
        return sessions.data or []
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération sessions")

@router.post("/sessions")
async def save_session(body: dict, cu: dict = Depends(get_current_user)):
    """Sauvegarde une nouvelle session de jeu."""
    try:
        # Mapper les noms du frontend vers les noms de la BDD
        session_data = {
            "user_id": cu["id"],
            "mode": body.get("slug") or body.get("mode", "unknown"),
            "score": body.get("score", 0),
            "total_hits": body.get("total_hits", 0),
            "combo_max": body.get("max_combo", 0),  # ✅ combo_max pas max_combo
            "avg_force_g": body.get("avg_force_g", 0),
            "max_force_g": body.get("max_force_g", 0),
            "avg_reaction_ms": body.get("avg_reaction", 0),  # ✅ avg_reaction_ms pas avg_reaction
            "duration_s": body.get("duration_s", 0),
            "xp_gained": body.get("xp_earned", 0),  # ✅ xp_gained pas xp_earned
            "avg_speed_kmh": body.get("avg_speed_kmh", 0),
            "avg_force_n": body.get("avg_force_n", 0),
            "total_shots": body.get("total_shots", 0),
            "total_score": body.get("total_score", 0),
            "total_misses": body.get("total_misses", 0),
            "precision_rate": body.get("precision_rate", 0),
            "avg_vitesse": body.get("avg_vitesse", 0),
        }
        
        result = supabase.table("sessions").insert(session_data).execute()
        
        # Mettre à jour le XP du joueur
        xp_earned = body.get("xp_earned", 0)
        if xp_earned > 0:
            profile = supabase.table("users").select("xp").eq("id", cu["id"]).execute()
            if profile.data:
                current_xp = profile.data[0].get("xp") or 0
                supabase.table("users").update({"xp": current_xp + xp_earned}).eq("id", cu["id"]).execute()
        
        return {"session_id": result.data[0]["id"] if result.data else None, "message": "Session sauvegardée"}
    except Exception as e:
        logger.error(f"Save session error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde: {e}")