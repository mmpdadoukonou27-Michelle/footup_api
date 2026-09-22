import uuid
from database.supabase_client import supabase
from core.security import hash_password, verify_password, create_access_token
from core.exceptions import UserAlreadyExists, InvalidCredentials

async def register_user(email: str, password: str, name: str = None, role: str = "player"):
    if supabase.table("users").select("id").eq("email", email).execute().data:
        raise UserAlreadyExists()
    
    res = supabase.table("users").insert({
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "role": role,
        "user_id": str(uuid.uuid4()),
        "level": "debutant",
        "xp": 0
    }).execute()
    
    if not res.data:
        raise Exception("Erreur création BDD")
    
    u = res.data[0]
    u.pop("password_hash", None)
    token = create_access_token({"user_id": u["id"], "role": u.get("role")})
    return {"token": token, "user": u}

async def login_user(email: str, password: str):
    res = supabase.table("users").select("*").eq("email", email).execute()
    if not res.data or not verify_password(password, res.data[0]["password_hash"]):
        raise InvalidCredentials()
    
    u = res.data[0]
    token = create_access_token({"user_id": u["id"], "role": u.get("role")})
    u.pop("password_hash", None)
    return {"token": token, "user": u}