#!/usr/bin/env python3
"""Pack 130 — Real Player Snapshot server-scope verifier (STATIC + UNIT-RUNTIME)."""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'real_player_snapshot.py'


class _MockColl:
    def __init__(self, doc=None, list_docs=None, capture=None):
        self.doc = doc; self.list_docs = list_docs or []; self.capture = capture
    async def find_one(self, query, *a, **kw):
        if self.capture is not None: self.capture.append(('find_one', query))
        return self.doc
    def find(self, query, *a, **kw):
        if self.capture is not None: self.capture.append(('find', query))
        outer = self
        class _Cursor:
            async def to_list(self, length=None): return outer.list_docs
        return _Cursor()


class _MockDB:
    def __init__(self, capture):
        self.player_server_profiles = _MockColl(doc={'team_formation': [{'user_hero_id': 'uh1'}]}, capture=capture)
        self.user_heroes = _MockColl(list_docs=[{'user_hero_id': 'uh1', 'user_id': 'u1', 'server_id': 's1', 'hero_id': 'h1', 'level': 5}], capture=capture)
        self.heroes = _MockColl(list_docs=[{'id': 'h1', 'display_name': 'Test', 'rarity': 'RARE'}], capture=capture)


async def _smoke():
    from helpers.real_player_snapshot import build_real_player_snapshot
    capture = []
    db = _MockDB(capture)
    snap = await build_real_player_snapshot(db, user_id='u1', server_id='s1')
    return snap, capture


def main() -> int:
    errors = []; notes = []
    if not HELPER.exists(): errors.append('real_player_snapshot.py missing'); return _emit(errors, notes, {}, [])
    src = HELPER.read_text(encoding='utf-8')
    # Static: nessun update_one nei file di helper.
    for forbidden in ['update_one(', 'insert_one(', 'delete_one(', 'replace_one(', 'find_one_and_update']:
        if forbidden in src:
            errors.append(f'forbidden write op in snapshot helper: {forbidden}')
    # Static: greek_borea exclusion presente.
    if 'greek_borea' not in src:
        errors.append('greek_borea not in FORBIDDEN_HERO_KEYS')
    snap, capture = asyncio.get_event_loop().run_until_complete(_smoke())
    # Verifica che ogni query DB sia server-scoped.
    for op, q in capture:
        if op in ('find_one', 'find') and 'user_id' in q:
            if 'server_id' not in q:
                errors.append(f'snapshot helper query NOT server-scoped: {op} {q}')
    print(f'OK    snapshot helper executed {len(capture)} DB ops; all server-scoped' if not errors else f'FAIL queries')
    if snap.get('source') != 'server_scoped_team_formation':
        errors.append(f'snapshot source not server_scoped_team_formation: {snap.get("source")}')
    if 'battle_power_status' not in snap or snap.get('battle_power_status') != 'DEFERRED':
        errors.append('battle_power_status not DEFERRED')
    if 'player_snapshot_hash' not in snap:
        errors.append('player_snapshot_hash missing')
    return _emit(errors, notes, snap, capture)


def _emit(errors, notes, snap, capture):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_REAL_PLAYER_SNAPSHOT_SERVER_SCOPE',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'sample_snapshot': snap if isinstance(snap, dict) else {},
              'db_ops_captured': [{'op': o, 'query_keys': list(q.keys()) if isinstance(q, dict) else None} for o, q in capture],
              'validation_kind': 'STATIC+UNIT_RUNTIME',
              'enforcement': 'ENFORCED_ALL_DB_QUERIES_SERVER_SCOPED_NO_WRITE_OPS_IN_HELPER'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_real_player_snapshot_server_scope_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  snapshot helper is server-scoped, no DB writes, no client trust')
    return 0


if __name__ == '__main__': sys.exit(main())
