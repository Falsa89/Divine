"""Pack 131 — Snapshot-to-Combat preview adapter (read-only).

Consuma il real player snapshot Pack 130 (build_real_player_snapshot) e
produce un combat preview input compatibile con QA preview — no battle_engine
execution, no reward, no progress, no DB write.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict
from .real_player_snapshot import _hash_snapshot

DEFAULT_DUMMY_ENEMY = {
    'source': 'PACK_131_PLACEHOLDER_DUMMY',
    'team_b_status': 'PLACEHOLDER_DETERMINISTIC',
    'heroes': [],
}


def build_combat_preview_input(player_snapshot: Dict[str, Any], *, mode: str, server_id: str) -> Dict[str, Any]:
    team_a = []
    for h in (player_snapshot or {}).get('heroes', []) or []:
        if h.get('snapshot_status') != 'OK':
            continue
        team_a.append({
            'user_hero_id': h.get('user_hero_id'),
            'hero_id': h.get('hero_id'),
            'level': h.get('level'),
            'stars': h.get('stars'),
            'rarity': h.get('rarity'),
            'element': h.get('element'),
            'slot': h.get('slot'),
        })
    payload = {
        'combat_preview_input': {
            'source': 'PACK_130_REAL_PLAYER_SNAPSHOT',
            'team_a': team_a,
            'team_b': DEFAULT_DUMMY_ENEMY,
            'team_b_status': 'PLACEHOLDER_OR_DEFERRED',
            'mode': mode,
            'server_id': server_id,
            'preview_only': True,
            'authoritative': False,
        },
        'input_snapshot_hash': _hash_snapshot(team_a),
        'player_snapshot_hash': player_snapshot.get('player_snapshot_hash', ''),
        'battle_engine_execution_status': 'BATTLE_ENGINE_EXECUTION_DEFERRED',
        'combat_consumption_status': 'PACK_131_PREVIEW_ONLY',
        'reward_status': 'DISABLED',
        'exp_status': 'DISABLED',
        'progress_status': 'DISABLED',
    }
    return payload


def build_post_battle_preview() -> Dict[str, Any]:
    return {
        'post_battle_preview': {
            'preview_only': True,
            'authoritative': False,
            'claim_enabled': False,
            'reward_status': 'DISABLED',
            'exp_status': 'DISABLED',
            'progress_status': 'DISABLED',
            'inventory_mutation': False,
            'economy_mutation': False,
            'hero_progression_mutation': False,
            'potential_rewards_preview_only': [],
            'not_granted': True,
            'claim_disabled': True,
            'next_gate': 'PACK_132_OR_LATER',
        }
    }
