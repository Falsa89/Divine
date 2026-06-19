"""Pack 130 — Lobby Launch Context router (READ-ONLY).

Endpoint:
  GET /api/lobby/launch-context/preview?mode=training&server_id=s1

Properties:
  - auth-required (Bearer JWT, stesso schema usato da server.py)
  - server-scoped (server_ready_guard Pack 129)
  - read-only (no DB write)
  - real player snapshot da player_server_profiles + user_heroes server-scoped
  - enemy snapshot DEFERRED
  - combat consumption DEFERRED a Pack 131
  - structured errors Pack 129 contract
"""
from __future__ import annotations

import os
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Query

router = APIRouter(prefix="/api/lobby", tags=["lobby_launch_v130"])

_JWT_SECRET = os.getenv("JWT_SECRET", "divine_waifus_secret_key_2025")


async def _resolve_user(authorization: Optional[str]) -> Optional[dict]:
    """Replica leggera di server.get_current_user per evitare circular import.
    Stesso schema Bearer JWT HS256, stesso secret env.
    """
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


@router.get("/launch-context/preview")
async def lobby_launch_context_preview(
    mode: str = Query(default='training'),
    server_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    """Pack 130 — launch context preview, read-only.

    Args via query:
      mode: una delle training/story/boss/tower/event/arena.
      server_id: server context corrente del player (richiesto).
    """
    current_user = await _resolve_user(authorization)
    user_id = current_user.get('id') if current_user else None
    # Lazy import per evitare cicli al boot.
    from server import db as _db
    from helpers.lobby_launch_context import build_lobby_launch_context
    result = await build_lobby_launch_context(_db, user_id=user_id, server_id=server_id, mode=mode)
    if not result.get('ok'):
        raise HTTPException(
            status_code=result.get('status_code', 400),
            detail=result.get('detail'),
        )
    return result
