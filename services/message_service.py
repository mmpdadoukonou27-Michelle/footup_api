import logging
from typing import Optional
from database.supabase_client import supabase
from services.push_service import send_push

logger = logging.getLogger(__name__)

async def get_unread_count(user_id: int):
    res = supabase.table("messages").select("id", count="exact").eq("receiver_id", user_id).eq("read", False).execute()
    return {"count": res.count or 0}

async def get_conversations(user_id: int):
    res = supabase.table("messages").select("*").or_(f"sender_id.eq.{user_id},receiver_id.eq.{user_id}").order("created_at", desc=True).execute()
    seen = set()
    convs = []
    for msg in (res.data or []):
        oid = msg["receiver_id"] if msg["sender_id"] == user_id else msg["sender_id"]
        if oid in seen:
            continue
        seen.add(oid)
        ur = supabase.table("messages").select("id", count="exact").eq("sender_id", oid).eq("receiver_id", user_id).eq("read", False).execute()
        fr = supabase.table("users").select("id,name,avatar_url").eq("id", oid).execute()
        fi = fr.data[0] if fr.data else {}
        convs.append({
            "friend_id": str(oid),
            "name": fi.get("name", "Joueur"),
            "avatar_url": fi.get("avatar_url"),
            "last_message": msg["content"],
            "last_message_at": msg["created_at"],
            "unread_count": ur.count or 0,
            "is_online": False
        })
    return convs

async def get_messages(user_id: int, friend_id: int):
    res = supabase.table("messages").select("*").or_(
        f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id}),and(sender_id.eq.{friend_id},receiver_id.eq.{user_id})"
    ).order("created_at", desc=False).limit(50).execute()
    return [{
        "id": str(m["id"]),
        "sender_id": str(m["sender_id"]),
        "receiver_id": str(m["receiver_id"]),
        "content": m["content"],
        "read": m["read"],
        "created_at": m["created_at"]
    } for m in (res.data or [])]

async def get_conversation_status(user_id: int, friend_id: int):
    """Récupère le statut d'amitié + s'il y a une demande de conversation en attente."""
    
    # Statut d'amitié
    friend_check = supabase.table("friends_challenges").select("status, user_id").or_(
        f"and(user_id.eq.{user_id},friend_id.eq.{friend_id}),and(user_id.eq.{friend_id},friend_id.eq.{user_id})"
    ).execute()
    
    friend_status = "none"
    if friend_check.data:
        row = friend_check.data[0]
        if row["status"] == "accepted":
            friend_status = "accepted"
        elif row["user_id"] == user_id:
            friend_status = "pending"
        else:
            friend_status = "incoming"
    
    # Vérifier s'il y a une demande de conversation
    conv_req = supabase.table("conversation_requests").select("*").or_(
        f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id}),and(sender_id.eq.{friend_id},receiver_id.eq.{user_id})"
    ).eq("status", "pending").execute()
    
    conversation_request = None
    if conv_req.data:
        conversation_request = conv_req.data[0]
    
    return {
        "friend_status": friend_status,
        "conversation_request": conversation_request,
        "can_message": friend_status == "accepted" or (conversation_request and conversation_request["status"] == "accepted")
    }

async def send_message(user_id: int, friend_id: int, content: str, sender_name: str = "Coéquipier"):
    """Envoie un message. Si non-amis, crée une demande de conversation."""
    
    if not content.strip():
        raise ValueError("Message vide")
    
    # Vérifier le statut
    status_res = await get_conversation_status(user_id, friend_id)
    friend_status = status_res["friend_status"]
    
    # CAS 1 : Amis → message direct
    if friend_status == "accepted":
        res = supabase.table("messages").insert({
            "sender_id": user_id,
            "receiver_id": friend_id,
            "content": content.strip(),
            "read": False
        }).execute()
        if not res.data:
            raise Exception("Erreur envoi")
        
        m = res.data[0]
        await send_push(friend_id, f"💬 {sender_name}", 
                       content.strip()[:80], 
                       {"type": "message", "from_user_id": user_id})
        return {
            "id": str(m["id"]),
            "sender_id": str(m["sender_id"]),
            "receiver_id": str(m["receiver_id"]),
            "content": m["content"],
            "read": m["read"],
            "created_at": m["created_at"]
        }
    
    # CAS 2 : Non-amis → créer une demande de conversation
    existing = supabase.table("conversation_requests").select("*").or_(
        f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id}),and(sender_id.eq.{friend_id},receiver_id.eq.{user_id})"
    ).execute()
    
    if existing.data and existing.data[0]["status"] == "pending":
        raise Exception("Demande de conversation déjà envoyée. En attente de réponse.")
    
    # Créer la demande de conversation
    conv_req = supabase.table("conversation_requests").insert({
        "sender_id": user_id,
        "receiver_id": friend_id,
        "first_message": content.strip(),
        "status": "pending"
    }).execute()
    
    if not conv_req.data:
        raise Exception("Erreur création demande de conversation")
    
    # Envoyer une notification push
    await send_push(friend_id, f"📩 {sender_name}", 
                   f"Demande de conversation : {content.strip()[:60]}...", 
                   {"type": "conversation_request", "from_user_id": user_id, "request_id": conv_req.data[0]["id"]})
    
    return {
        "type": "conversation_request",
        "status": "pending",
        "request_id": conv_req.data[0]["id"],
        "message": "Demande de conversation envoyée. En attente d'acceptation."
    }

async def mark_read(user_id: int, friend_id: int):
    supabase.table("messages").update({"read": True}).eq("sender_id", friend_id).eq("receiver_id", user_id).eq("read", False).execute()
    return {"message": "OK"}

# ─── GESTION DES DEMANDES DE CONVERSATION ─────────────────

async def get_conversation_requests(user_id: int):
    """Récupère les demandes de conversation reçues."""
    res = supabase.table("conversation_requests").select("*").eq("receiver_id", user_id).eq("status", "pending").execute()
    
    if not res.data:
        return []
    
    # Enrichir avec les infos utilisateur
    sender_ids = [r["sender_id"] for r in res.data]
    users = {u["id"]: u for u in (supabase.table("users").select("id,name,avatar_url").in_("id", sender_ids).execute().data or [])}
    
    return [{
        "request_id": r["id"],
        "sender_id": r["sender_id"],
        "name": users.get(r["sender_id"], {}).get("name"),
        "avatar_url": users.get(r["sender_id"], {}).get("avatar_url"),
        "first_message": r["first_message"],
        "created_at": r["created_at"]
    } for r in res.data]

async def accept_conversation_request(request_id: str, user_id: int, accepter_name: str = "Quelquun"):
    """Accepte une demande de conversation et envoie le premier message."""
    
    req = supabase.table("conversation_requests").select("*").eq("id", request_id).eq("receiver_id", user_id).eq("status", "pending").execute()
    
    if not req.data:
        raise Exception("Demande introuvable")
    
    request = req.data[0]
    
    # Accepter la demande
    supabase.table("conversation_requests").update({"status": "accepted"}).eq("id", request_id).execute()
    
    # Envoyer le premier message (celui qui était en attente)
    res = supabase.table("messages").insert({
        "sender_id": request["sender_id"],
        "receiver_id": user_id,
        "content": request["first_message"],
        "read": True
    }).execute()
    
    # Notifier l'expéditeur
    await send_push(request["sender_id"], "✅ Demande acceptée", 
                   f"{accepter_name} a accepté votre conversation.", 
                   {"type": "conversation_accepted", "from_user_id": user_id})
    
    return {"message": "Conversation acceptée"}

async def decline_conversation_request(request_id: str, user_id: int):
    """Refuse une demande de conversation."""
    supabase.table("conversation_requests").delete().eq("id", request_id).eq("receiver_id", user_id).execute()
    return {"message": "Demande refusée"}

async def share_session(user_id: int, friend_id: int, session_id: str, message: str = None, sender_name: str = "Coéquipier"):
    """Partage une session dans une conversation."""
    
    # Vérifier que la session existe et appartient à l'utilisateur
    session = supabase.table("sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
    if not session.data:
        raise Exception("Session introuvable")
    
    s = session.data[0]
    
    # Créer le message formaté
    share_text = f"🏆 Session partagée !\n"
    share_text += f"Score: {s.get('total_score', s.get('score', 0))} pts\n"
    share_text += f"Précision: {s.get('precision_rate', 0)}%\n"
    share_text += f"Tirs: {s.get('total_shots', s.get('total_hits', 0))}\n"
    if s.get('avg_speed_kmh'):
        share_text += f"Vitesse: {s.get('avg_speed_kmh')} km/h\n"
    if s.get('avg_force_n'):
        share_text += f"Force: {s.get('avg_force_n')}N\n"
    
    if message:
        share_text = f"{message}\n\n{share_text}"
    
    # Envoyer comme message normal
    return await send_message(user_id, friend_id, share_text, sender_name)