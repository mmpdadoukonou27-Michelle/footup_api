from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from services.leaderboard_service import get_global_leaderboard, get_friends_leaderboard

router = APIRouter()

@router.get("/leaderboard")
async def global_leaderboard():
    try:
        return await get_global_leaderboard()
    except Exception as e:
        raise HTTPException(500, "Erreur calcul classement")

@router.get("/friends/leaderboard")
async def friends_leaderboard(cu: dict = Depends(get_current_user)):
    try:
        return await get_friends_leaderboard(cu["id"])
    except Exception as e:
        raise HTTPException(500, "Erreur classement amis")