"""Pack 131 — Combat Preview route (GET, read-only).
GET /api/combat/preview?mode=training&server_id=qa-eu-01
"""
from __future__ import annotations
import os
from typing import Optional
import jwt
from fastapi import APIRouter, Header, HTTPException, Query

router = APIRouter(prefix="/api/combat", tags=["combat_preview_v131"])
from helpers.jwt_secret_preflight import resolve_jwt_secret  # SECURITY_HOTFIX_A
_JWT_SECRET = resolve_jwt_secret()
from helpers.server_id_contract import validate_psp_server_id


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


@router.get("/preview")
async def combat_preview(
    mode: str = Query(default='training'),
    server_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    """Pack 131 / HOTFIX F — combat preview READ-ONLY.

    Consuma `team_formation_v1` da launch_context (HOTFIX E contract):
      - user_hero_id resta owned id primario;
      - canonical_id è solo catalog metadata;
      - blocca su missing/empty/ambiguous V1;
      - NESSUNA chiamata a /api/battle/simulate (Hotfix A fail-closed BE);
      - NESSUN reward / progress / battle_engine.
    """
    current_user = await _resolve_user(authorization)
    user_id = current_user.get('id')
    validation = await validate_psp_server_id(server_id)
    if not validation.ok:
        raise HTTPException(
            status_code=validation.http_status,
            detail={
                'blocker': validation.blocker,
                'server_id': validation.server_id,
                'allowlist_source': validation.allowlist_source,
                'reason': validation.reason,
                'route': '/api/combat/preview',
            },
        )
    server_id = validation.server_id
    from server import db as _db
    from helpers.lobby_launch_context import build_lobby_launch_context
    from helpers.combat_preview_adapter import build_combat_preview_input, build_post_battle_preview
    launch = await build_lobby_launch_context(_db, user_id=user_id, server_id=server_id, mode=mode)
    if not launch.get('ok'):
        raise HTTPException(status_code=launch.get('status_code', 400), detail=launch.get('detail'))
    snap = launch.get('player_snapshot', {})
    # HOTFIX F — Estrazione + blocking su team_formation_v1.
    team_formation_v1 = snap.get('team_formation_v1') or []
    team_formation_v1_warnings = snap.get('team_formation_v1_warnings') or []
    if not isinstance(team_formation_v1, list):
        raise HTTPException(
            status_code=400,
            detail={
                'blocker': 'COMBAT_PREVIEW_TEAMFORMATION_V1_REQUIRED',
                'message': 'team_formation_v1 mancante dal launch context.',
                'route': '/api/combat/preview',
            },
        )
    if len(team_formation_v1) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                'blocker': 'COMBAT_PREVIEW_TEAMFORMATION_V1_EMPTY',
                'message': 'team_formation_v1 vuota: combat preview non costruibile.',
                'team_formation_v1_warnings': team_formation_v1_warnings,
                'route': '/api/combat/preview',
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
                'blocker': 'COMBAT_PREVIEW_TEAMFORMATION_V1_AMBIGUOUS',
                'message': 'Almeno uno slot legacy non disambiguabile in V1.',
                'ambiguous_warnings': ambiguous,
                'route': '/api/combat/preview',
            },
        )
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
        # HOTFIX F — esposizione V1 al top-level del preview per consumer FE.
        'team_formation_v1': team_formation_v1,
        'team_formation_v1_warnings': team_formation_v1_warnings,
        'team_formation_v1_size': len(team_formation_v1),
        'hotfix_f_combat_preview_consumes_v1': True,
        # Lock attivi (Hotfix A + Hotfix F preview-only invariant).
        'reward_status': 'DISABLED',
        'progress_status': 'DISABLED',
        'battle_simulate_status': 'BLOCKED_PRE_QA_HOTFIX_A_FAIL_CLOSED',
        'combat_preview_reward_lock_active': True,
        **combat_input,
        **post,
        'device_qa_status': 'BLOCKED',
        'pack_origin': 'PACK_131',
    }
