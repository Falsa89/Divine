#!/usr/bin/env python3
"""
CS2-A — Collection Synergies V2 Readiness Audit (READ-ONLY)
────────────────────────────────────────────────────────────────────────
Reports on current Team Synergy V2 state, Codex/Hero Detail UI shape, and the
readiness plan + optional draft schema for future Collection Synergy V2
activation. Strict read-only. No DB / runtime / catalog changes.
"""
from __future__ import annotations
import json, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data/design/synergies/collection_synergies_v2_readiness_plan_v1.json'
SCHEMA = ROOT / 'data/design/synergies/collection_synergy_v2_schema_draft_v1.json'
TEAM_V2 = ROOT / 'data/design/team_synergies_v2_initial_10.json'
ROUTES = ROOT / 'backend/routes/synergies.py'
DEFS_MODULE = ROOT / 'backend/data/synergy_definitions_v2.py'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
UI_CODEX = ROOT / 'frontend/app/synergy-codex.tsx'
UI_HERO_DETAIL = ROOT / 'frontend/app/hero-detail.tsx'
API = 'http://localhost:8001/api'

failures, warnings, infos = [], [], []
def fail(s, m): failures.append(f'[{s}] {m}')
def warn(s, m): warnings.append(f'[{s}] {m}')
def info(m): infos.append(m)


def http_get(path, timeout=5.0):
    try:
        with urllib.request.urlopen(API + path, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None

FORBIDDEN_UI_TOKENS = ('Activate', 'Claim', 'Spend', 'Equip', 'Battle Test',
                       'Enable Runtime', "onPress={activate", "onPress={claim",
                       "onPress={spend", "method: 'POST'", "method: \"POST\"",
                       "method: 'PUT'", "method: 'PATCH'", "method: 'DELETE'")
FORBIDDEN_RUNTIME_GREP_IN_BATTLE = ('collection_synergy_resolve', 'apply_collection_synergy_buff',
                                    'COLLECTION_SYNERGY_BATTLE_ENABLED = True')


def main() -> int:
    if not PLAN.exists():
        fail('plan', f'readiness plan missing: {PLAN}')
        return emit('FAIL')
    try:
        plan = json.loads(PLAN.read_text(encoding='utf-8'))
    except Exception as e:
        fail('plan', f'parse error: {e}')
        return emit('FAIL')
    for k, want in (('design_only', True), ('runtime_attached', False),
                    ('battle_runtime_attached', False), ('db_write', False),
                    ('no_borea_activation', True), ('no_runtime_feature_flag_on', True)):
        if plan.get(k) is not want:
            fail('plan', f'{k} != {want}')
    if plan.get('task_origin') != 'CS2-A':
        fail('plan', 'task_origin != CS2-A')
    cats = plan.get('proposed_collection_synergy_categories') or []
    cat_ids = {c.get('id') for c in cats}
    expected_cats = {'faction_collection', 'element_collection', 'rarity_collection',
                     'origin_group_collection', 'mythic_set_collection',
                     'divine_weapon_collection_link_future'}
    if cat_ids != expected_cats:
        fail('plan', f'category set mismatch: extra={cat_ids - expected_cats} missing={expected_cats - cat_ids}')
    # max cap policy sanity
    mm = plan.get('proposed_milestone_model') or {}
    if mm.get('max_total_collection_bonus_pct', 999) > 15:
        fail('plan', f'max_total_collection_bonus_pct > 15')
    if mm.get('max_per_category_bonus_pct', 999) > 5:
        fail('plan', f'max_per_category_bonus_pct > 5')

    # schema draft (optional)
    if SCHEMA.exists():
        try:
            sch = json.loads(SCHEMA.read_text(encoding='utf-8'))
            for k, want in (('design_only', True), ('runtime_attached', False),
                            ('battle_runtime_attached', False), ('db_write', False),
                            ('loaded_by_runtime', False)):
                if sch.get(k) is not want:
                    fail('schema', f'{k} != {want}')
            inv = sch.get('validation_invariants') or {}
            if inv.get('max_total_bonus_pct') != 15:
                fail('schema', 'max_total_bonus_pct != 15')
        except Exception as e:
            fail('schema', f'parse: {e}')
        info('schema draft present')

    # Team Synergy V2 source
    if TEAM_V2.exists():
        try:
            d = json.loads(TEAM_V2.read_text(encoding='utf-8'))
            syn = d if isinstance(d, list) else (d.get('synergies') or d.get('definitions') or [])
            info(f'team_synergies_v2_initial_10 count = {len(syn) if isinstance(syn, list) else "N/A"}')
        except Exception as e:
            warn('team_v2', f'parse: {e}')
    else:
        warn('team_v2', 'team_synergies_v2_initial_10.json not found')

    # Routes: read-only check (no POST/PUT/PATCH/DELETE)
    if ROUTES.exists():
        t = ROUTES.read_text(encoding='utf-8', errors='ignore')
        for verb in ('@router.post(', '@router.put(', '@router.patch(', '@router.delete('):
            if verb in t:
                # tolerated only if outside synergies (paranoia: this file is the synergies router)
                fail('routes', f'{ROUTES.name} contains {verb}')
        info('synergies routes: no POST/PUT/PATCH/DELETE')
    else:
        warn('routes', 'synergies.py not found')

    # Battle engine: must not apply collection synergy buff
    if BATTLE_ENGINE.exists():
        t = BATTLE_ENGINE.read_text(encoding='utf-8', errors='ignore')
        for tok in FORBIDDEN_RUNTIME_GREP_IN_BATTLE:
            if tok in t:
                fail('battle_engine', f'{tok!r} present in battle_engine.py')
        info('battle_engine.py: no collection synergy hook')

    # UI: codex and hero detail
    # Token check is CONTEXTUAL: forbidden tokens only count when they appear on a
    # line that also mentions synergy/collection/affinity/gift — so we don't false-
    # positive on pre-existing unrelated features (runes equipment, etc.).
    context_keywords = ('synerg', 'collection', 'affinity', 'gift')
    for f in (UI_CODEX, UI_HERO_DETAIL):
        if not f.exists():
            warn('ui', f'{f.name} not found')
            continue
        t = f.read_text(encoding='utf-8', errors='ignore')
        lines = t.split('\n')
        for tok in FORBIDDEN_UI_TOKENS:
            for ln_no, line in enumerate(lines, 1):
                if tok in line and any(ck in line.lower() for ck in context_keywords):
                    fail('ui', f'{f.name}:L{ln_no} contains forbidden token {tok!r} in synergy/collection/affinity context')
        info(f'{f.name}: no activate/claim/spend Pressable in synergy/collection/affinity context')

    # API smoke
    code, _ = http_get('/heroes')
    if code != 200:
        warn('api', f'/api/heroes status {code}')
    else:
        info('/api/heroes 200')
    code, body = http_get('/synergies/v2/all')
    if code == 200:
        info('/api/synergies/v2/all 200')
    elif code == 401:
        info('/api/synergies/v2/all auth-gated (401)')
    else:
        warn('api', f'/synergies/v2/all status {code}')
    code, _ = http_get('/synergies/by_hero/greek_borea')
    if code in (200, 401, 404):
        info(f'/synergies/by_hero/greek_borea status {code} (acceptable; auth-gated or hidden)')
    else:
        warn('api', f'/synergies/by_hero/greek_borea unexpected {code}')

    return emit('PASS' if not failures else 'FAIL')


def emit(result):
    print('=' * 72)
    print('CS2-A Collection Synergies V2 Readiness Audit')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print('\nFAILURES:')
        for f in failures: print(f'  - {f}')
    print(f'\nRESULT: {result}')
    return 0 if result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
