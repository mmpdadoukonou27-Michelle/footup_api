from database.supabase_client import supabase

async def update_user_profile(user_id: int, update_data: dict):
    if not update_data:
        raise ValueError("Aucune donnée")
    res = supabase.table("users").update(update_data).eq("id", user_id).execute()
    if not res.data:
        raise Exception("Erreur mise à jour")
    u = res.data[0]
    u.pop("password_hash", None)
    return u

async def delete_user_account(user_id: int):
    supabase.table("users").delete().eq("id", user_id).execute()
    return {"message": "Compte supprimé"}

async def save_push_token(user_id: int, token: str):
    supabase.table("users").update({"push_token": token}).eq("id", user_id).execute()
    return {"message": "Token enregistré"}