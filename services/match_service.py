from database.supabase_client import supabase
from datetime import datetime, timezone
import uuid

async def create_match(player1_id: int, player2_id: int):
    """Crée un match entre deux joueurs."""
    match = supabase.table("live_matches").insert({
        "player1_id": player1_id,
        "player2_id": player2_id,
        "status": "waiting"
    }).execute()
    return match.data[0] if match.data else None

async def join_match(match_id: str, player_id: int):
    """Rejoint un match en attente."""
    match = supabase.table("live_matches").select("*").eq("id", match_id).execute()
    if not match.data:
        return None
    
    m = match.data[0]
    if m["player1_id"] == player_id:
        # Le créateur rejoint
        supabase.table("live_matches").update({"status": "active"}).eq("id", match_id).execute()
    elif m["player2_id"] == player_id:
        # L'adversaire rejoint
        supabase.table("live_matches").update({"status": "active"}).eq("id", match_id).execute()
    
    return m

async def update_score(match_id: str, player_id: int, score: int, data: dict = {}):
    """Met à jour le score d'un joueur."""
    match = supabase.table("live_matches").select("*").eq("id", match_id).execute()
    if not match.data:
        return None
    
    m = match.data[0]
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if m["player1_id"] == player_id:
        update_data["player1_score"] = score
        update_data["player1_data"] = data
    elif m["player2_id"] == player_id:
        update_data["player2_score"] = score
        update_data["player2_data"] = data
    
    supabase.table("live_matches").update(update_data).eq("id", match_id).execute()
    return True

async def finish_match(match_id: str, winner_id: int):
    """Termine un match."""
    supabase.table("live_matches").update({
        "status": "finished",
        "winner_id": winner_id
    }).eq("id", match_id).execute()
    