"""Pack 130 — Lobby Launch Context router (READ-ONLY).

Endpoint:
  GET /api/lobby/launch-context/preview?mode=training&server_id=qa-eu-01

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

from helpers.jwt_secret_preflight import resolve_jwt_secret  # SECURITY_HOTFIX_A
_JWT_SECRET = resolve_jwt_secret()
from helpers.server_id_contract import validate_psp_server_id


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
    from server import db as _db, _latest_logout_cutoff, _token_issued_at
    issued_at = _token_issued_at(payload)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token non valido")
    user = await _db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    logout_cutoff = _latest_logout_cutoff(user)
    if logout_cutoff and issued_at < logout_cutoff:
        raise HTTPException(status_code=401, detail="Token revocato")
    return user


@router.get("/launch-context/preview")
async def lobby_launch_context_preview(
    mode: str = Query(default='training'),
    server_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    """Pack 130 — launch context preview, read-only.
    HOTFIX F — esposizione + blocking su `team_formation_v1` (HOTFIX E
    contract). Refuse-by-default se la V1 risulta missing/empty/ambiguous.

    Args via query:
      mode: una delle training/story/boss/tower/event/arena.
      server_id: server context corrente del player (richiesto).
    """
    current_user = await _resolve_user(authorization)
    user_id = current_user.get('id') if current_user else None
    validation = await validate_psp_server_id(server_id)
    if not validation.ok:
        raise HTTPException(
            status_code=validation.http_status,
            detail={
                'blocker': validation.blocker,
                'server_id': validation.server_id,
                'allowlist_source': validation.allowlist_source,
                'reason': validation.reason,
                'route': '/api/lobby/launch-context/preview',
            },
        )
    server_id = validation.server_id
    # Lazy import per evitare cicli al boot.
    from server import db as _db
    from helpers.lobby_launch_context import build_lobby_launch_context
    result = await build_lobby_launch_context(_db, user_id=user_id, server_id=server_id, mode=mode)
    if not result.get('ok'):
        raise HTTPException(
            status_code=result.get('status_code', 400),
            detail=result.get('detail'),
        )
    # HOTFIX F — Estrai team_formation_v1 dallo snapshot Pack 130 (esposto
    # da HOTFIX E in `real_player_snapshot.build_real_player_snapshot`).
    snapshot = result.get('player_snapshot') or {}
    team_formation_v1 = snapshot.get('team_formation_v1') or []
    team_formation_v1_warnings = snapshot.get('team_formation_v1_warnings') or []
    # Refuse-by-default: blocca se la V1 è missing/empty/ambiguous.
    if not isinstance(team_formation_v1, list):
        raise HTTPException(
            status_code=400,
            detail={
                'blocker': 'LOBBY_TEAMFORMATION_V1_REQUIRED',
                'message': 'team_formation_v1 mancante dallo snapshot.',
                'route': '/api/lobby/launch-context/preview',
            },
        )
    if len(team_formation_v1) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                'blocker': 'LOBBY_TEAMFORMATION_V1_EMPTY',
                'message': 'team_formation_v1 è vuoto dopo normalizzazione HOTFIX E.',
                'team_formation_v1_warnings': team_formation_v1_warnings,
                'route': '/api/lobby/launch-context/preview',
            },
        )
    ambiguous = [
        w for w in team_formation_v1_warnings
        if isinstance(w, dict) and w.get('blocker') == 'TEAM_FORMATION_LEGACY_AMBIGUOUS'
    ]
    if ambiguous:
        raise HTTPException(
            status_code=409,
            detail={
                'blocker': 'LOBBY_TEAMFORMATION_V1_AMBIGUOUS',
                'message': 'Almeno uno slot legacy non disambiguabile in V1.',
                'ambiguous_warnings': ambiguous,
                'route': '/api/lobby/launch-context/preview',
            },
        )
    # Propaga V1 al top-level per visibility downstream (combat preview,
    # frontend pre-battle-lobby). user_hero_id resta owned id primario;
    # canonical_id è metadata. NO DB writes, NO reward, NO mutations.
    result['team_formation_v1'] = team_formation_v1
    result['team_formation_v1_warnings'] = team_formation_v1_warnings
    result['team_formation_v1_size'] = len(team_formation_v1)
    result['hotfix_f_lobby_consumes_v1'] = True
    result['reward_status'] = 'DISABLED'
    result['progress_status'] = 'DISABLED'
    return result
