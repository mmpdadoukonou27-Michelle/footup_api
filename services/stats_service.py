from database.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

async def get_user_stats(user_id: int):
    """Récupère les stats d'un utilisateur avec les VRAIS noms de colonnes."""
    try:
        sessions = supabase.table("sessions").select(
            "total_score, avg_force_n, precision_rate, total_shots, avg_speed_kmh, score, total_hits, avg_force_g, max_force_g, avg_reaction_ms, duration_s, xp_gained, combo_max"
        ).eq("user_id", user_id).execute().data or []
        
        n = len(sessions)
        if n == 0:
            return {
                "total_sessions": 0,
                "avg_power": 0,
                "total_shots": 0,
                "total_score": 0,
                "avg_speed": 0
            }

        return {
            "total_sessions": n,
            "avg_power": round(sum(s.get("avg_force_n") or 0 for s in sessions) / n, 1),
            "total_shots": sum(s.get("total_shots") or 0 for s in sessions),
            "total_score": sum(s.get("total_score") or s.get("score") or 0 for s in sessions),
            "avg_speed": round(sum(s.get("avg_speed_kmh") or 0 for s in sessions) / n, 1),
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "total_sessions": 0,
            "avg_power": 0,
            "total_shots": 0,
            "total_score": 0,
            "avg_speed": 0
        }