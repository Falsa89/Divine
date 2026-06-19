"""Pack 130 — Lobby Launch Context builder (read-only).

Produce un launch context sicuro per la lobby pre-combat:
  - server-scoped (usa Pack 129 server_ready_guard);
  - auth-required (gestito a livello di route);
  - real player snapshot (usa Pack 130 real_player_snapshot);
  - enemy_snapshot_status: DEFERRED_TO_PACK_131_OR_LATER;
  - combat_consumption_status: DEFERRED_TO_PACK_131;
  - reward_status: DISABLED;
  - progress_status: DISABLED.

NON tocca DB write. NON avvia battle_engine. NON genera enemy live.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

from .real_player_snapshot import build_real_player_snapshot, _hash_snapshot
from .server_ready_guard import check_server_ready, STATE_READY, state_to_structured_code
from .structured_errors import (
    AUTH_REQUIRED, build_structured_detail,
)

ALLOWED_MODES = ('training', 'story', 'boss', 'tower', 'event', 'arena')

# Codici structured aggiuntivi per Pack 130 (logici, non costanti separate per
# evitare duplicazione — i nuovi codici sono testabili e documentati nel marker).
LOBBY_MODE_INVALID = 'LOBBY_MODE_INVALID'
LOBBY_MODE_NOT_READY_PRE_QA = 'LOBBY_MODE_NOT_READY_PRE_QA'
LAUNCH_CONTEXT_BLOCKED_PRE_QA = 'LAUNCH_CONTEXT_BLOCKED_PRE_QA'
SNAPSHOT_BUILD_FAILED = 'SNAPSHOT_BUILD_FAILED'
TEAM_FORMATION_MISSING = 'TEAM_FORMATION_MISSING'
TEAM_FORMATION_EMPTY = 'TEAM_FORMATION_EMPTY'
COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131 = 'COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131'


async def build_lobby_launch_context(
    db,
    *,
    user_id: Optional[str],
    server_id: Optional[str],
    mode: str,
) -> Dict[str, Any]:
    """Costruisce il launch context. Ritorna sempre un dict; mai raise.

    Il caller (route) usa il campo `status_code` per decidere HTTP status,
    e `detail` (structured) per il body.

    Ritorno (success):
      {
        'ok': True, 'launch_context_id': ..., 'mode': ..., 'server_id': ...,
        'user_id': ..., 'player_snapshot': {...},
        'enemy_snapshot_status': 'DEFERRED_TO_PACK_131_OR_LATER',
        'combat_consumption_status': 'DEFERRED_TO_PACK_131',
        'reward_status': 'DISABLED', 'progress_status': 'DISABLED',
        'device_qa_status': 'BLOCKED', 'launch_context_hash': '...'
      }
    Ritorno (error):
      {'ok': False, 'status_code': int, 'detail': {<structured>}}
    """
    route = '/api/lobby/launch-context/preview'
    method = 'GET'
    if not user_id:
        return {'ok': False, 'status_code': 401,
                'detail': build_structured_detail(
                    detail='Autenticazione richiesta per launch context',
                    code=AUTH_REQUIRED, route=route, method=method,
                    recoverable=True)}
    # Mode check
    if mode not in ALLOWED_MODES:
        return {'ok': False, 'status_code': 400,
                'detail': build_structured_detail(
                    detail=f'Mode `{mode}` non consentita in pre-QA',
                    code=LOBBY_MODE_INVALID, category='validation',
                    route=route, method=method,
                    extra={'allowed_modes': list(ALLOWED_MODES)},
                    recoverable=True)}
    # Server ready guard (Pack 129)
    state, info = await check_server_ready(db, user_id, server_id)
    if state != STATE_READY:
        code = state_to_structured_code(state)
        return {'ok': False, 'status_code': 400 if state in ('SERVER_CONTEXT_MISSING', 'SERVER_CONTEXT_INVALID', 'SERVER_MISMATCH') else 404,
                'detail': build_structured_detail(
                    detail=f'Server context non pronto: {state}',
                    code=code, route=route, method=method,
                    extra={'state': state, 'info': info}, recoverable=True)}
    # Real player snapshot (read-only)
    snapshot = await build_real_player_snapshot(db, user_id, server_id or '')
    snap_status = snapshot.get('snapshot_status', 'OK')
    if snap_status == 'TEAM_FORMATION_MISSING':
        return {'ok': False, 'status_code': 404,
                'detail': build_structured_detail(
                    detail='Team formation mancante per questo server',
                    code=TEAM_FORMATION_MISSING, category='team',
                    route=route, method=method, recoverable=True)}
    if snap_status == 'TEAM_FORMATION_EMPTY':
        return {'ok': False, 'status_code': 400,
                'detail': build_structured_detail(
                    detail='Team formation vuota',
                    code=TEAM_FORMATION_EMPTY, category='team',
                    route=route, method=method, recoverable=True)}
    if snap_status == 'SNAPSHOT_BUILD_FAILED':
        return {'ok': False, 'status_code': 503,
                'detail': build_structured_detail(
                    detail='Snapshot build fallita',
                    code=SNAPSHOT_BUILD_FAILED, category='server',
                    route=route, method=method, recoverable=True,
                    extra={'reason': snapshot.get('error')})}
    # Build success response
    launch_context_id = hashlib.sha256(
        f'{user_id}:{server_id}:{mode}:{snapshot.get("player_snapshot_hash", "")}'
        .encode('utf-8')
    ).hexdigest()[:24]
    response = {
        'ok': True,
        'launch_context_id': launch_context_id,
        'mode': mode,
        'server_id': server_id,
        'user_id': user_id,  # not redacted in pre-QA (caller-only)
        'player_snapshot': snapshot,
        'enemy_snapshot_status': 'DEFERRED_TO_PACK_131_OR_LATER',
        'combat_consumption_status': COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131,
        'reward_status': 'DISABLED',
        'progress_status': 'DISABLED',
        'device_qa_status': 'BLOCKED',
        'pack_origin': 'PACK_130',
    }
    response['launch_context_hash'] = _hash_snapshot(response)
    return response
