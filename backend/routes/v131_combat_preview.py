"""Pack 131 — Combat Preview route (GET, read-only).
GET /api/combat/preview?mode=training&server_id=s1
"""
from __future__ import annotations
import os
from typing import Optional
import jwt
from fastapi import APIRouter, Header, HTTPException, Query

router = APIRouter(prefix="/api/combat", tags=["combat_preview_v131"])
from helpers.jwt_secret_preflight import resolve_jwt_secret  # SECURITY_HOTFIX_A
_JWT_SECRET = resolve_jwt_secret()


async def _resolve_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")
    from server import db as _db
    user = await _db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    return user


@router.get("/preview")
async def combat_preview(
    mode: str = Query(default='training'),
    server_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    current_user = await _resolve_user(authorization)
    user_id = current_user.get('id')
    from server import db as _db
    from helpers.lobby_launch_context import build_lobby_launch_context
    from helpers.combat_preview_adapter import build_combat_preview_input, build_post_battle_preview
    launch = await build_lobby_launch_context(_db, user_id=user_id, server_id=server_id, mode=mode)
    if not launch.get('ok'):
        raise HTTPException(status_code=launch.get('status_code', 400), detail=launch.get('detail'))
    snap = launch.get('player_snapshot', {})
    combat_input = build_combat_preview_input(snap, mode=mode, server_id=server_id or '')
    post = build_post_battle_preview()
    return {
        'ok': True,
        'preview_battle_id': launch.get('launch_context_id'),
        'launch_context_id': launch.get('launch_context_id'),
        'mode': mode,
        'server_id': server_id,
        'preview_only': True,
        'authoritative': False,
        **combat_input,
        **post,
        'device_qa_status': 'BLOCKED',
        'pack_origin': 'PACK_131',
    }
