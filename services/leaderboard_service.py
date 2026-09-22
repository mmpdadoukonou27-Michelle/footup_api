import logging
from database.supabase_client import supabase

logger = logging.getLogger(__name__)

async def compute_leaderboard_data(user_ids: list):
    if not user_ids:
        return []
    
    users_res = supabase.table("users").select("id, name, club, avatar_url, position, xp").in_("id", user_ids).execute()
    users_data = users_res.data or []
    leaderboard = []
    
    try:
        sessions_res = supabase.table("sessions").select(
            "user_id, total_score, avg_force_n, precision_rate, total_shots, avg_speed_kmh, score, total_hits"
        ).in_("user_id", user_ids).execute()
        all_sessions = sessions_res.data or []
    except Exception as e:
        logger.warning(f"Sessions query failed: {e}")
        all_sessions = []
    
    for u in users_data:
        user_sessions = [s for s in all_sessions if s["user_id"] == u["id"]]
        n = len(user_sessions)
        score = sum(s.get("total_score") or s.get("score") or 0 for s in user_sessions)
        total_shots = sum(s.get("total_shots") or s.get("total_hits") or 0 for s in user_sessions)
        avg_power = round(sum(s.get("avg_force_n") or 0 for s in user_sessions) / max(n, 1), 1)
        avg_speed = round(sum(s.get("avg_speed_kmh") or 0 for s in user_sessions) / max(n, 1), 1)
        
        leaderboard.append({
            **u,
            "score": score if score > 0 else u.get("xp", 0),
            "total_sessions": n,
            "total_shots": total_shots,
            "avg_power": avg_power,
            "avg_speed": avg_speed,
        })
    
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard

async def get_global_leaderboard():
    top_users = supabase.table("users").select("id").order("xp", desc=True).limit(50).execute()
    ids = [u["id"] for u in (top_users.data or [])]
    return await compute_leaderboard_data(ids)

async def get_friends_leaderboard(user_id: int):
    sent = supabase.table("friends_challenges").select("friend_id").eq("user_id", user_id).eq("status", "accepted").execute()
    received = supabase.table("friends_challenges").select("user_id").eq("friend_id", user_id).eq("status", "accepted").execute()
    friend_ids = [r["friend_id"] for r in (sent.data or [])] + [r["user_id"] for r in (received.data or [])]
    friend_ids.append(user_id)
    return await compute_leaderboard_data(friend_ids)