import logging
import httpx
from database.supabase_client import supabase

logger = logging.getLogger(__name__)

async def send_push(to_user_id: int, title: str, body: str, data: dict = {}):
    try:
        res = supabase.table("users").select("push_token").eq("id", to_user_id).execute()
        token = res.data[0].get("push_token") if res.data else None
        if not token or not token.startswith("ExponentPushToken"):
            return
        async with httpx.AsyncClient() as c:
            await c.post(
                "https://exp.host/--/api/v2/push/send",
                json={"to": token, "title": title, "body": body, "data": data, "sound": "default"},
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
    except Exception as e:
        logger.warning(f"Push failed: {e}")