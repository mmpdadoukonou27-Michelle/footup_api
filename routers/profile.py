import uuid
import logging
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from models.profile import ProfileUpdate
from database.supabase_client import supabase
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile")
async def get_profile(cu: dict = Depends(get_current_user)):
    return cu

@router.put("/profile")
async def update_profile(data: ProfileUpdate, cu: dict = Depends(get_current_user)):
    from services.profile_service import update_user_profile
    try:
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        return await update_user_profile(cu["id"], update_data)
    except ValueError:
        raise HTTPException(400, "Aucune donnée")
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), cu: dict = Depends(get_current_user)):
    try:
        content = await file.read()
        ext = (file.filename or "avatar.jpg").split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            ext = "jpg"
        path = f"{cu['id']}_{uuid.uuid4()}.{ext}"
        old = cu.get("avatar_url", "")
        if old and "avatars/" in old:
            try:
                supabase.storage.from_("avatars").remove([old.split("/object/avatars/")[-1].split("?")[0]])
            except:
                pass
        ct = file.content_type or ("image/png" if ext == "png" else "image/jpeg")
        supabase.storage.from_("avatars").upload(path, content, {"content-type": ct})
        url = supabase.storage.from_("avatars").get_public_url(path)
        supabase.table("users").update({"avatar_url": url}).eq("id", cu["id"]).execute()
        return {"avatar_url": url}
    except Exception as e:
        logger.error(f"Avatar upload: {e}")
        raise HTTPException(500, f"Erreur upload: {e}")

@router.delete("/profile/avatar")
async def delete_avatar(cu: dict = Depends(get_current_user)):
    old = cu.get("avatar_url", "")
    if old and "avatars/" in old:
        try:
            supabase.storage.from_("avatars").remove([old.split("/object/avatars/")[-1].split("?")[0]])
        except:
            pass
    supabase.table("users").update({"avatar_url": None}).eq("id", cu["id"]).execute()
    return {"message": "Avatar supprimé"}

@router.delete("/users/me")
async def delete_account(cu: dict = Depends(get_current_user)):
    from services.profile_service import delete_user_account
    return await delete_user_account(cu["id"])