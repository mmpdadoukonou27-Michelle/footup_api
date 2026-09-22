from fastapi import APIRouter, HTTPException, Depends
from models.auth import UserRegister, UserLogin
from services.auth_service import register_user, login_user
from services.profile_service import save_push_token
from dependencies import get_current_user

router = APIRouter()

@router.post("/auth/register")
@router.post("/register")
async def register(user: UserRegister):
    try:
        return await register_user(user.email, user.password, user.name, user.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/auth/login")
async def login(user: UserLogin):
    try:
        return await login_user(user.email, user.password)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/auth/me")
async def auth_me(cu: dict = Depends(get_current_user)):
    return cu

@router.post("/auth/logout")
async def logout():
    return {"message": "Déconnecté"}

@router.post("/auth/push-token")
async def save_push_token_route(body, cu: dict = Depends(get_current_user)):
    # Note: import PushTokenUpdate in production
    return await save_push_token(cu["id"], body.push_token)

@router.post("/auth/request-password-reset")
async def reset_pw(cu: dict = Depends(get_current_user)):
    return {"message": "Email envoyé"}