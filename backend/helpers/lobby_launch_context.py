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
from functools import lru_cache
from pathlib import Path
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
STORY_SOURCE_TYPE = 'story_stage_encounter_table'
STORY_ENEMY_SOURCE_TYPE = 'authored'
STORY_ENCOUNTER_PARAMS_REQUIRED = 'STORY_ENCOUNTER_PARAMS_REQUIRED'
STORY_ENCOUNTER_NOT_FOUND = 'STORY_ENCOUNTER_NOT_FOUND'
STORY_SOURCE_TYPE_MISMATCH = 'STORY_SOURCE_TYPE_MISMATCH'
STORY_SOURCE_ID_MISMATCH = 'STORY_SOURCE_ID_MISMATCH'
STORY_ENCOUNTER_ID_MISMATCH = 'STORY_ENCOUNTER_ID_MISMATCH'
STORY_ENEMY_SOURCE_TYPE_MISMATCH = 'STORY_ENEMY_SOURCE_TYPE_MISMATCH'
STORY_ENEMY_SOURCE_ID_MISMATCH = 'STORY_ENEMY_SOURCE_ID_MISMATCH'
STORY_CHAPTER_ID_MISMATCH = 'STORY_CHAPTER_ID_MISMATCH'
STORY_STAGE_MISMATCH = 'STORY_STAGE_MISMATCH'


def _clean_param(value: Optional[str]) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _story_stage_parts(encounter: Dict[str, Any]) -> tuple[str, str]:
    stage_id = _clean_param(encounter.get('stage_id'))
    if '-' not in stage_id:
        return '', stage_id
    chapter, stage = stage_id.split('-', 1)
    return chapter, stage


@lru_cache(maxsize=1)
def _load_story_encounter_catalog() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    catalog_path = root / 'data' / 'design' / 'battle_mode_enemy_sources' / 'story_encounter_stub_catalog_v1.json'
    with catalog_path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def _story_failure(code: str, detail: str, route: str, method: str, *, extra: Optional[dict] = None) -> Dict[str, Any]:
    return {
        'ok': False,
        'status_code': 400 if code != STORY_ENCOUNTER_NOT_FOUND else 404,
        'detail': build_structured_detail(
            detail=detail,
            code=code,
            category='validation' if code != STORY_ENCOUNTER_NOT_FOUND else 'not_found',
            route=route,
            method=method,
            extra=extra,
            recoverable=True,
        ),
    }


def _resolve_story_encounter(
    *,
    source_type: Optional[str],
    source_id: Optional[str],
    encounter_id: Optional[str],
    enemy_source_type: Optional[str],
    enemy_source_id: Optional[str],
    chapter_id: Optional[str],
    stage: Optional[str],
    route: str,
    method: str,
) -> Dict[str, Any]:
    params = {
        'source_type': _clean_param(source_type),
        'source_id': _clean_param(source_id),
        'encounter_id': _clean_param(encounter_id),
        'enemy_source_type': _clean_param(enemy_source_type),
        'enemy_source_id': _clean_param(enemy_source_id),
        'chapter_id': _clean_param(chapter_id),
        'stage': _clean_param(stage),
    }
    required = [key for key, value in params.items() if not value]
    if required:
        return _story_failure(
            STORY_ENCOUNTER_PARAMS_REQUIRED,
            'Parametri Story mancanti per launch context',
            route,
            method,
            extra={'missing': required},
        )
    if params['source_type'] != STORY_SOURCE_TYPE:
        return _story_failure(
            STORY_SOURCE_TYPE_MISMATCH,
            'source_type Story non coerente con il catalog',
            route,
            method,
            extra={'expected': STORY_SOURCE_TYPE, 'actual': params['source_type']},
        )
    if params['enemy_source_type'] != STORY_ENEMY_SOURCE_TYPE:
        return _story_failure(
            STORY_ENEMY_SOURCE_TYPE_MISMATCH,
            'enemy_source_type Story non coerente con il catalog',
            route,
            method,
            extra={'expected': STORY_ENEMY_SOURCE_TYPE, 'actual': params['enemy_source_type']},
        )

    catalog = _load_story_encounter_catalog()
    encounters = catalog.get('encounters') or []
    match = next(
        (
            item for item in encounters
            if item.get('source_type') == STORY_SOURCE_TYPE
            and item.get('source_id') == params['source_id']
            and item.get('encounter_id') == params['encounter_id']
        ),
        None,
    )
    if not match:
        return _story_failure(
            STORY_ENCOUNTER_NOT_FOUND,
            'Encounter Story non trovato nel catalog',
            route,
            method,
            extra={'source_id': params['source_id'], 'encounter_id': params['encounter_id']},
        )

    if match.get('source_id') != params['source_id']:
        return _story_failure(
            STORY_SOURCE_ID_MISMATCH,
            'source_id Story non coerente con il catalog',
            route,
            method,
            extra={'expected': match.get('source_id'), 'actual': params['source_id']},
        )
    if match.get('encounter_id') != params['encounter_id']:
        return _story_failure(
            STORY_ENCOUNTER_ID_MISMATCH,
            'encounter_id Story non coerente con il catalog',
            route,
            method,
            extra={'expected': match.get('encounter_id'), 'actual': params['encounter_id']},
        )
    if params['enemy_source_id'] != params['source_id']:
        return _story_failure(
            STORY_ENEMY_SOURCE_ID_MISMATCH,
            'enemy_source_id Story non coerente con source_id canonico',
            route,
            method,
            extra={'expected': params['source_id'], 'actual': params['enemy_source_id']},
        )

    chapter, stage_value = _story_stage_parts(match)
    if params['chapter_id'] != chapter:
        return _story_failure(
            STORY_CHAPTER_ID_MISMATCH,
            'chapter_id Story non coerente con stage_id catalog',
            route,
            method,
            extra={'expected': chapter, 'actual': params['chapter_id']},
        )
    if params['stage'] != stage_value:
        return _story_failure(
            STORY_STAGE_MISMATCH,
            'stage Story non coerente con stage_id catalog',
            route,
            method,
            extra={'expected': stage_value, 'actual': params['stage']},
        )

    canonical = dict(match)
    canonical['chapter_id'] = chapter
    canonical['stage'] = stage_value
    canonical['enemy_source_type'] = STORY_ENEMY_SOURCE_TYPE
    canonical['enemy_source_id'] = canonical.get('source_id')
    return {'ok': True, 'encounter': canonical}


async def build_lobby_launch_context(
    db,
    *,
    user_id: Optional[str],
    server_id: Optional[str],
    mode: str,
    source_type: Optional[str] = None,
    source_id: Optional[str] = None,
    encounter_id: Optional[str] = None,
    enemy_source_type: Optional[str] = None,
    enemy_source_id: Optional[str] = None,
    chapter_id: Optional[str] = None,
    stage: Optional[str] = None,
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
    story_encounter = None
    if mode == 'story':
        story_resolution = _resolve_story_encounter(
            source_type=source_type,
            source_id=source_id,
            encounter_id=encounter_id,
            enemy_source_type=enemy_source_type,
            enemy_source_id=enemy_source_id,
            chapter_id=chapter_id,
            stage=stage,
            route=route,
            method=method,
        )
        if not story_resolution.get('ok'):
            return story_resolution
        story_encounter = story_resolution.get('encounter') or {}
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
    canonical_source_id = story_encounter.get('source_id') if story_encounter else source_id
    canonical_encounter_id = story_encounter.get('encounter_id') if story_encounter else encounter_id
    canonical_source_type = story_encounter.get('source_type') if story_encounter else source_type
    canonical_enemy_source_type = story_encounter.get('enemy_source_type') if story_encounter else enemy_source_type
    canonical_enemy_source_id = story_encounter.get('enemy_source_id') if story_encounter else enemy_source_id
    canonical_chapter_id = story_encounter.get('chapter_id') if story_encounter else chapter_id
    canonical_stage = story_encounter.get('stage') if story_encounter else stage
    launch_context_id = hashlib.sha256(
        f'{user_id}:{server_id}:{mode}:{canonical_source_id or ""}:{canonical_encounter_id or ""}:{snapshot.get("player_snapshot_hash", "")}'
        .encode('utf-8')
    ).hexdigest()[:24]
    launch_context = {
        'launch_context_id': launch_context_id,
        'server_id': server_id,
        'mode': mode,
        'source_type': canonical_source_type,
        'source_id': canonical_source_id,
        'encounter_id': canonical_encounter_id,
        'enemy_source_type': canonical_enemy_source_type,
        'enemy_source_id': canonical_enemy_source_id,
        'chapter_id': canonical_chapter_id,
        'stage': canonical_stage,
        'is_preview': True,
        'reward_policy': 'preview',
        'progress_policy': 'preview',
        'battle_engine_mode': 'preview',
        'player_snapshot': snapshot,
        'team_formation_v1': snapshot.get('team_formation_v1') or [],
        'enemy_source_metadata': story_encounter,
    }
    response = {
        'ok': True,
        'launch_context_id': launch_context_id,
        'mode': mode,
        'server_id': server_id,
        'source_type': canonical_source_type,
        'source_id': canonical_source_id,
        'encounter_id': canonical_encounter_id,
        'enemy_source_type': canonical_enemy_source_type,
        'enemy_source_id': canonical_enemy_source_id,
        'chapter_id': canonical_chapter_id,
        'stage': canonical_stage,
        'user_id': user_id,  # not redacted in pre-QA (caller-only)
        'player_snapshot': snapshot,
        'launch_context': launch_context,
        'enemy_snapshot_status': 'DEFERRED_TO_PACK_131_OR_LATER',
        'combat_consumption_status': COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131,
        'is_preview': True,
        'reward_policy': 'preview',
        'progress_policy': 'preview',
        'battle_engine_mode': 'preview',
        'reward_status': 'DISABLED',
        'progress_status': 'DISABLED',
        'device_qa_status': 'BLOCKED',
        'pack_origin': 'PACK_130',
    }
    response['launch_context_hash'] = _hash_snapshot(response)
    return response
