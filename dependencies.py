from typing import Optional
from fastapi import Header, HTTPException
from database.supabase_client import supabase
from core.security import jwt_decode

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    try:
        payload = jwt_decode(authorization.split(" ")[1])
        res = supabase.table("users").select("*").eq("id", payload.get("user_id")).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        u = res.data[0]
        u.pop("password_hash", None)
        return u
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Session invalide")