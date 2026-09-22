from database.supabase_client import supabase
from services.push_service import send_push

async def get_friends(user_id: int):
    sent = supabase.table("friends_challenges").select("friend_id").eq("user_id", user_id).eq("status", "accepted").execute()
    recv = supabase.table("friends_challenges").select("user_id").eq("friend_id", user_id).eq("status", "accepted").execute()
    ids = [r["friend_id"] for r in (sent.data or [])] + [r["user_id"] for r in (recv.data or [])]
    if not ids:
        return []
    return supabase.table("users").select("id,name,avatar_url,club,position").in_("id", ids).execute().data or []

async def get_friend_requests(user_id: int):
    pending = supabase.table("friends_challenges").select("id,user_id,created_at").eq("friend_id", user_id).eq("status", "pending").execute()
    if not pending.data:
        return []
    ids = [r["user_id"] for r in pending.data]
    users = {u["id"]: u for u in (supabase.table("users").select("id,name,avatar_url,club").in_("id", ids).execute().data or [])}
    return [{
        "request_id": r["id"],
        "user_id": r["user_id"],
        "name": users.get(r["user_id"], {}).get("name"),
        "avatar_url": users.get(r["user_id"], {}).get("avatar_url"),
        "club": users.get(r["user_id"], {}).get("club"),
        "created_at": r["created_at"]
    } for r in pending.data]

async def send_request(user_id: int, target_user_id: int, sender_name: str = "Quelquun"):
    ex = supabase.table("friends_challenges").select("id,status").or_(
        f"and(user_id.eq.{user_id},friend_id.eq.{target_user_id}),and(user_id.eq.{target_user_id},friend_id.eq.{user_id})"
    ).execute()
    if ex.data:
        st = ex.data[0]["status"]
        if st == "accepted":
            raise Exception("Vous êtes déjà amis.")
        if st == "pending":
            raise Exception("Demande déjà envoyée.")
    
    supabase.table("friends_challenges").insert({
        "user_id": user_id,
        "friend_id": target_user_id,
        "status": "pending"
    }).execute()
    
    await send_push(target_user_id, "Nouvelle demande de coequipier",
                    f"{sender_name} veut vous ajouter comme coequipier !",
                    {"type": "friend_request", "from_user_id": user_id})
    return {"message": "Demande envoyée"}

async def accept_request(request_id: int, user_id: int, accepter_name: str = "Quelquun"):
    req = supabase.table("friends_challenges").select("*").eq("id", request_id).eq("friend_id", user_id).execute()
    if not req.data:
        raise Exception("Demande introuvable")
    
    supabase.table("friends_challenges").update({"status": "accepted"}).eq("id", request_id).execute()
    
    await send_push(req.data[0]["user_id"], "Demande acceptee !",
                    f"{accepter_name} a accepte votre demande de coequipier.",
                    {"type": "friend_accepted", "from_user_id": user_id})
    return {"message": "Demande acceptée"}

async def decline_request(request_id: int, user_id: int):
    supabase.table("friends_challenges").delete().eq("id", request_id).eq("friend_id", user_id).execute()
    return {"message": "Demande refusée"}

async def remove_friend(user_id: int, friend_id: int):
    supabase.table("friends_challenges").delete().or_(
        f"and(user_id.eq.{user_id},friend_id.eq.{friend_id}),and(user_id.eq.{friend_id},friend_id.eq.{user_id})"
    ).execute()
    return {"message": "Ami supprimé"}

async def search_users(query: str, exclude_id: int):
    if len(query) < 2:
        return []
    return supabase.table("users").select("id,name,avatar_url,club,position").ilike("name", f"%{query}%").neq("id", exclude_id).limit(20).execute().data or []

async def get_friend_status(user_id: int, other_id: int):
    """Récupère le statut d'amitié entre deux utilisateurs."""
    check = supabase.table("friends_challenges").select("status, user_id").or_(
        f"and(user_id.eq.{user_id},friend_id.eq.{other_id}),and(user_id.eq.{other_id},friend_id.eq.{user_id})"
    ).execute()
    if not check.data:
        return "none"
    row = check.data[0]
    if row["status"] == "accepted":
        return "accepted"
    return "pending" if row["user_id"] == user_id else "incoming"