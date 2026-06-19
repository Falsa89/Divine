"""Pack 130 — Real Player Snapshot builder (read-only).

Legge team_formation da player_server_profiles e i corrispondenti user_heroes
filtrati per server_id; produce uno snapshot sanitizzato dei dati eroe
sicuro per la lobby pre-combat. NON modifica DB. NON tocca reward/economy/
progress/inventory. NON si fida del client.

Uscita: dict con shape:
  {
    'source': 'server_scoped_team_formation',
    'team_size': int,
    'heroes': [
      {'user_hero_id', 'hero_id', 'slot' {col,row}, 'level', 'stars',
       'ascension', 'rarity', 'element', 'role', 'faction', 'display_name',
       'asset_key', 'snapshot_status'},
      ...
    ],
    'battle_power_status': 'DEFERRED',
    'player_snapshot_hash': 'sha256_hex_short',
  }
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

# Campi safe che possiamo esporre per ogni hero snapshot.
SAFE_HERO_FIELDS = (
    'user_hero_id', 'hero_id', 'canonical_id', 'level', 'stars', 'ascension',
    'rarity', 'element', 'role', 'faction', 'display_name',
    'asset_key', 'asset_status',
)

# Campi mai esposti (sensibili / authoritative).
FORBIDDEN_HERO_FIELDS = (
    'drop_table', 'reward_rate', 'admin_flags', 'debug', 'secret',
    'battle_power_client_computed', 'raw_stats_authoritative',
    'gacha_rate', 'shop_price', 'economy_internal',
)

# Marker noti per esclusione (Borea / legacy hidden).
FORBIDDEN_HERO_KEYS = (
    'greek_borea',  # hidden / pending_assets
)


def _safe_int(v: Any, default: int = 1) -> int:
    try:
        n = int(v)
        if n < 0: return default
        return n
    except Exception:
        return default


def _sanitize_hero(uh: Dict[str, Any], canonical: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Estrae solo i campi safe dall'oggetto user_hero (+canonical) per lo snapshot.
    Ritorna None se l'eroe è forbidden/hidden o non ha id."""
    if not isinstance(uh, dict):
        return None
    hero_id = uh.get('hero_id') or (canonical or {}).get('hero_id') or (canonical or {}).get('id')
    if not hero_id:
        return None
    if hero_id in FORBIDDEN_HERO_KEYS:
        return None
    # Bonus check: se canonical dichiara asset_status=pending_assets o
    # contract_status=pending_contract, escludiamo (Borea-style).
    if canonical:
        if str(canonical.get('asset_status', '')).startswith('pending'):
            return None
        if str(canonical.get('contract_status', '')).startswith('pending'):
            return None
    out = {
        'user_hero_id': uh.get('user_hero_id') or uh.get('id'),
        'hero_id': hero_id,
        'canonical_id': (canonical or {}).get('id') or hero_id,
        'level': _safe_int(uh.get('level'), 1),
        'stars': _safe_int(uh.get('stars'), 1),
        'ascension': _safe_int(uh.get('ascension'), 0),
        'rarity': uh.get('rarity') or (canonical or {}).get('rarity', 'UNKNOWN'),
        'element': uh.get('element') or (canonical or {}).get('element', 'NONE'),
        'role': uh.get('role') or (canonical or {}).get('role', 'NONE'),
        'faction': uh.get('faction') or (canonical or {}).get('faction', 'NONE'),
        'display_name': (canonical or {}).get('display_name') or uh.get('display_name') or hero_id,
        'asset_key': (canonical or {}).get('asset_key') or uh.get('asset_key', ''),
        'asset_status': (canonical or {}).get('asset_status', 'unknown'),
        'snapshot_status': 'OK',
    }
    # Defensive: rimuovi qualsiasi key in FORBIDDEN_HERO_FIELDS che sia
    # accidentalmente colata via spread.
    for k in FORBIDDEN_HERO_FIELDS:
        out.pop(k, None)
    return out


def _hash_snapshot(payload: Dict[str, Any]) -> str:
    """Hash deterministico (sha256, primi 16 char) dello snapshot per debug."""
    try:
        ser = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        ser = repr(payload)
    return hashlib.sha256(ser.encode('utf-8')).hexdigest()[:16]


async def build_real_player_snapshot(
    db,
    user_id: str,
    server_id: str,
) -> Dict[str, Any]:
    """Costruisce uno snapshot reale del team server-scoped per (user_id, server_id).

    Comportamento:
      - Legge PSP per ottenere team_formation;
      - Legge user_heroes filtrato per (user_id, server_id) per le statistiche;
      - Legge canonical heroes da `heroes` collection per display fields;
      - Sanitizza ogni hero via _sanitize_hero;
      - Calcola team_size dopo sanitizzazione;
      - Ritorna dict snapshot.

    Casi limite:
      - team_formation vuota → heroes=[], team_size=0, status='EMPTY';
      - team_formation None → status='MISSING';
      - DB error → status='SNAPSHOT_BUILD_FAILED'.
    """
    base = {
        'source': 'server_scoped_team_formation',
        'user_id': user_id,
        'server_id': server_id,
        'team_size': 0,
        'heroes': [],
        'battle_power_status': 'DEFERRED',
        'snapshot_status': 'OK',
    }
    try:
        psp = await db.player_server_profiles.find_one(
            {'user_id': user_id, 'server_id': server_id},
            projection={'_id': 0, 'team_formation': 1},
        )
    except Exception as e:
        base['snapshot_status'] = 'SNAPSHOT_BUILD_FAILED'
        base['error'] = f'PSP lookup failed: {e!r}'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base
    if not psp:
        base['snapshot_status'] = 'SERVER_PROFILE_MISSING'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base
    team_formation = psp.get('team_formation')
    if team_formation is None:
        base['snapshot_status'] = 'TEAM_FORMATION_MISSING'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base
    if isinstance(team_formation, list) and not team_formation:
        base['snapshot_status'] = 'TEAM_FORMATION_EMPTY'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base
    if not isinstance(team_formation, list):
        base['snapshot_status'] = 'TEAM_FORMATION_INVALID'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base

    # Estrai user_hero_ids dalla team_formation
    uh_ids: List[str] = []
    for entry in team_formation:
        if isinstance(entry, dict):
            uh = entry.get('user_hero_id') or entry.get('hero_id')
            if uh: uh_ids.append(str(uh))
    if not uh_ids:
        base['snapshot_status'] = 'TEAM_FORMATION_EMPTY'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base

    # Lookup user_heroes server-scoped (mai account-wide)
    try:
        user_heroes_cursor = db.user_heroes.find(
            {'user_id': user_id, 'server_id': server_id, '$or': [
                {'user_hero_id': {'$in': uh_ids}},
                {'id': {'$in': uh_ids}},
            ]},
            projection={'_id': 0},
        )
        user_heroes_raw = await user_heroes_cursor.to_list(length=20)
    except Exception as e:
        base['snapshot_status'] = 'SNAPSHOT_BUILD_FAILED'
        base['error'] = f'user_heroes lookup failed: {e!r}'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base
    if not user_heroes_raw:
        base['snapshot_status'] = 'TEAM_HERO_NOT_OWNED'
        base['player_snapshot_hash'] = _hash_snapshot(base)
        return base

    # Lookup canonical heroes (catalogo, read-only)
    hero_ids = sorted({uh.get('hero_id') for uh in user_heroes_raw if uh.get('hero_id')})
    try:
        canonical_cursor = db.heroes.find(
            {'$or': [{'id': {'$in': hero_ids}}, {'hero_id': {'$in': hero_ids}}]},
            projection={'_id': 0, 'id': 1, 'hero_id': 1, 'display_name': 1, 'rarity': 1,
                       'element': 1, 'role': 1, 'faction': 1, 'asset_key': 1, 'asset_status': 1,
                       'contract_status': 1},
        )
        canonical_list = await canonical_cursor.to_list(length=100)
        canonical_by_id = {c.get('id') or c.get('hero_id'): c for c in canonical_list}
    except Exception:
        canonical_by_id = {}

    # Mappa user_hero_id → slot dalla team_formation
    slot_by_uh_id: Dict[str, Any] = {}
    for entry in team_formation:
        if isinstance(entry, dict):
            uh = str(entry.get('user_hero_id') or entry.get('hero_id') or '')
            if uh:
                slot_by_uh_id[uh] = {
                    'col': entry.get('col') if entry.get('col') is not None else entry.get('column'),
                    'row': entry.get('row'),
                    'position': entry.get('position'),
                }

    # Build sanitized snapshot list
    snapshot_heroes: List[Dict[str, Any]] = []
    uh_by_id = {(uh.get('user_hero_id') or uh.get('id')): uh for uh in user_heroes_raw}
    for uh_id in uh_ids:
        uh = uh_by_id.get(uh_id) or uh_by_id.get(str(uh_id))
        if not uh:
            snapshot_heroes.append({
                'user_hero_id': uh_id,
                'snapshot_status': 'TEAM_HERO_NOT_OWNED',
            })
            continue
        canonical = canonical_by_id.get(uh.get('hero_id'))
        h = _sanitize_hero(uh, canonical)
        if h is None:
            snapshot_heroes.append({
                'user_hero_id': uh_id,
                'hero_id': uh.get('hero_id'),
                'snapshot_status': 'TEAM_HERO_NOT_AVAILABLE',
            })
            continue
        slot = slot_by_uh_id.get(str(uh_id), {})
        h['slot'] = slot
        snapshot_heroes.append(h)

    base['heroes'] = snapshot_heroes
    base['team_size'] = len([h for h in snapshot_heroes if h.get('snapshot_status') == 'OK'])
    if any(h.get('snapshot_status') in ('TEAM_HERO_NOT_OWNED', 'TEAM_HERO_NOT_AVAILABLE') for h in snapshot_heroes):
        base['snapshot_status'] = 'PARTIAL'
    base['player_snapshot_hash'] = _hash_snapshot(base)
    return base
