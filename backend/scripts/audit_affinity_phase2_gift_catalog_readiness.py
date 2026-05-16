#!/usr/bin/env python3
"""
AF2-A — Affinity Phase 2 Gift Catalog Readiness Audit (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Reports on current affinity surface and the readiness plan + optional draft
Faction × Element gift catalog. Strict read-only. No DB / runtime / catalog
changes.
"""
from __future__ import annotations
import json, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data/design/affinity/affinity_phase2_gift_catalog_readiness_plan_v1.json'
DRAFT = ROOT / 'data/design/affinity/affinity_gift_catalog_faction_element_draft_v1.json'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
ROUTES_DIR = ROOT / 'backend/routes'
FRONTEND_APP = ROOT / 'frontend/app'
API = 'http://localhost:8001/api'

failures, warnings, infos = [], [], []
def fail(s, m): failures.append(f'[{s}] {m}')
def warn(s, m): warnings.append(f'[{s}] {m}')
def info(m): infos.append(m)

FORBIDDEN_AFFINITY_TOKENS_IN_RUNTIME = (
    'apply_affinity_buff', 'affinity_stat_modifier', 'spend_gift_runtime',
    'AFFINITY_GIFT_RUNTIME_ENABLED = True',
)
FORBIDDEN_UI_AFFINITY_TOKENS = (
    'gift_claim', 'gift_spend', 'GiveGift', 'ClaimGift', 'SpendGift',
)
FORBIDDEN_ADULT_NAMING_SUBSTR = ('xxx', 'nsfw', 'lewd')


def http_get(path, timeout=5.0):
    try:
        with urllib.request.urlopen(API + path, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None


def main() -> int:
    if not PLAN.exists():
        fail('plan', f'plan missing: {PLAN}')
        return emit('FAIL')
    try:
        plan = json.loads(PLAN.read_text(encoding='utf-8'))
    except Exception as e:
        fail('plan', f'parse: {e}')
        return emit('FAIL')
    for k, want in (('design_only', True), ('runtime_attached', False),
                    ('db_write', False), ('no_borea_activation', True)):
        if plan.get(k) is not want:
            fail('plan', f'{k} != {want}')
    if plan.get('task_origin') != 'AF2-A':
        fail('plan', 'task_origin != AF2-A')
    sf = plan.get('safety_flags') or {}
    for k, want in (('runtime_attached', False), ('db_write', False),
                    ('inventory_mutation', False), ('borea_activation_allowed', False),
                    ('adult_explicit_naming', False),
                    ('feature_flag_currently_enabled', False)):
        if sf.get(k) is not want:
            fail('plan', f'safety_flags.{k} != {want}')

    # draft
    if DRAFT.exists():
        try:
            d = json.loads(DRAFT.read_text(encoding='utf-8'))
        except Exception as e:
            fail('draft', f'parse: {e}')
            d = None
        if d:
            if d.get('catalog_id') != 'affinity_gift_catalog_faction_element_draft_v1':
                fail('draft', 'catalog_id mismatch')
            for k, want in (('design_only', True), ('runtime_attached', False),
                            ('db_write', False), ('no_borea_activation', True)):
                if d.get(k) is not want:
                    fail('draft', f'{k} != {want}')
            entries = d.get('entries') or []
            facs = d.get('factions_used') or []
            elems = d.get('elements_used') or []
            expected_total = len(facs) * len(elems) + 1
            if len(entries) != expected_total:
                fail('draft', f'entries count {len(entries)} != expected {expected_total}')
            info(f'draft entries = {len(entries)} (factions={len(facs)} elements={len(elems)})')
            # constraints
            con = d.get('constraints') or {}
            for k, want in (
                ('no_stat_buffs_from_gifts_until_future_task', True),
                ('no_competitive_pvp_advantage_initial', True),
                ('borea_gifts_locked_until_visibility_unlock', True),
                ('adult_explicit_naming_forbidden', True),
                ('no_inventory_implementation_in_this_task', True),
                ('no_runtime_resolver_in_this_task', True),
            ):
                if con.get(k) is not want:
                    fail('draft', f'constraints.{k} != {want}')
            if con.get('pvp_cap_future_pct', 999) > 2:
                fail('draft', 'pvp_cap_future_pct > 2')
            if con.get('pvp_total_cap_future_pct', 999) > 6:
                fail('draft', 'pvp_total_cap_future_pct > 6')
            # per-entry assertions
            ids = set()
            for e in entries:
                if not isinstance(e, dict): fail('draft', 'non-dict entry'); continue
                gid = e.get('gift_id')
                if not gid or gid in ids:
                    fail('draft', f'dup or missing gift_id {gid!r}')
                ids.add(gid)
                for k, want in (('design_only', True), ('runtime_attached', False),
                                ('db_write', False), ('applied_to_combat', False),
                                ('no_stat_buff_until_future_approved_task', True),
                                ('borea_gift_locked_until_visibility_unlock', True),
                                ('no_competitive_pvp_advantage_initial', True),
                                ('naming_safe_for_rating', True)):
                    if e.get(k) is not want:
                        fail('draft', f'{gid}.{k} != {want}')
                low = (gid + ' ' + (e.get('display_name_localized_key_placeholder') or '')).lower()
                for s in FORBIDDEN_ADULT_NAMING_SUBSTR:
                    if s in low:
                        fail('draft', f'{gid}: forbidden adult-naming substring {s!r}')

    # battle_engine must not import affinity buffs
    if BATTLE_ENGINE.exists():
        t = BATTLE_ENGINE.read_text(encoding='utf-8', errors='ignore')
        for tok in FORBIDDEN_AFFINITY_TOKENS_IN_RUNTIME:
            if tok in t:
                fail('battle_engine', f'{tok!r} present in battle_engine.py')
        info('battle_engine.py: no affinity runtime hook')

    # routes: no spend/claim affinity endpoints
    if ROUTES_DIR.exists():
        for p in ROUTES_DIR.glob('*.py'):
            try:
                t = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for tok in ('/affinity/spend', '/affinity/claim', '/gift/spend', '/gift/claim'):
                if tok in t:
                    fail('routes', f'{p.name}: forbidden affinity endpoint token {tok!r}')

    # UI: no gift_claim/spend
    if FRONTEND_APP.exists():
        for p in FRONTEND_APP.glob('*.tsx'):
            try:
                t = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for tok in FORBIDDEN_UI_AFFINITY_TOKENS:
                if tok in t:
                    fail('ui', f'{p.name} contains forbidden gift token: {tok!r}')

    # API smoke
    code, _ = http_get('/heroes')
    if code != 200: warn('api', f'/api/heroes status {code}')
    else: info('/api/heroes 200')
    code, _ = http_get('/affinity/gifts')
    if code in (404, 401, -1):
        info(f'/api/affinity/gifts not exposed (status {code}) — expected')
    else:
        warn('api', f'/affinity/gifts unexpected status {code}')

    return emit('PASS' if not failures else 'FAIL')


def emit(result):
    print('=' * 72)
    print('AF2-A Affinity Phase 2 Gift Catalog Readiness Audit')
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
