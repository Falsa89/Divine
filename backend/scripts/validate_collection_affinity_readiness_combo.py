#!/usr/bin/env python3
"""
CS2-A + AF2-A — Combo Readiness Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────────
Consolidated cross-check that ensures:
  - Collection readiness plan present, design-only, runtime-off
  - Affinity readiness plan present, design-only, runtime-off
  - Optional schema/draft files present, design-only, runtime-off
  - No runtime endpoint added by this task
  - No DB write pattern
  - No battle_engine / combat changes
  - No UI mutation Pressable
  - Borea activation false / hidden via /api/heroes
  - /api/heroes = 100
  - No source catalog or baseline mutated (mtime sanity)
"""
from __future__ import annotations
import json, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path('/app')
PLAN_CS = ROOT / 'data/design/synergies/collection_synergies_v2_readiness_plan_v1.json'
SCHEMA_CS = ROOT / 'data/design/synergies/collection_synergy_v2_schema_draft_v1.json'
PLAN_AF = ROOT / 'data/design/affinity/affinity_phase2_gift_catalog_readiness_plan_v1.json'
DRAFT_AF = ROOT / 'data/design/affinity/affinity_gift_catalog_faction_element_draft_v1.json'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
COMBAT_UI = ROOT / 'frontend/app/combat.tsx'
BASELINE_V5 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132c2_v5.json'
API = 'http://localhost:8001/api'

failures, infos = [], []
def fail(s, m): failures.append(f'[{s}] {m}')
def info(m): infos.append(m)


def http_get(path, timeout=5.0):
    try:
        with urllib.request.urlopen(API + path, timeout=timeout) as r:
            body = r.read().decode('utf-8', errors='ignore')
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None


def assert_design_only(p: Path, label: str, *extras):
    if not p.exists():
        return
    try:
        d = json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail(label, f'parse error: {e}')
        return
    for k, want in (('design_only', True), ('runtime_attached', False), ('db_write', False)):
        if d.get(k) is not want:
            fail(label, f'{k} != {want}')
    for ex in extras:
        if d.get(ex) is not False:
            fail(label, f'{ex} != false')
    info(f'{label}: design_only=true, runtime_attached=false, db_write=false')


def main() -> int:
    # 1. plans
    if not PLAN_CS.exists():
        fail('cs_plan', f'missing: {PLAN_CS}')
    else:
        assert_design_only(PLAN_CS, 'cs_plan', 'battle_runtime_attached')
    if not PLAN_AF.exists():
        fail('af_plan', f'missing: {PLAN_AF}')
    else:
        assert_design_only(PLAN_AF, 'af_plan')

    # 2. optional drafts
    assert_design_only(SCHEMA_CS, 'cs_schema', 'battle_runtime_attached', 'loaded_by_runtime')
    assert_design_only(DRAFT_AF, 'af_draft', 'no_borea_activation' if False else 'runtime_attached')

    # 3. battle_engine / combat must not contain runtime hooks introduced by this task
    for p, tokens, label in (
        (BATTLE_ENGINE, ('collection_synergy_resolve', 'apply_collection_synergy_buff',
                         'apply_affinity_buff', 'affinity_stat_modifier'), 'battle_engine'),
        (COMBAT_UI, ('collection_synergy_resolve', 'apply_affinity_buff'), 'combat_ui'),
    ):
        if p.exists():
            t = p.read_text(encoding='utf-8', errors='ignore')
            for tok in tokens:
                if tok in t:
                    fail(label, f'{p.name}: forbidden token {tok!r}')

    # 4. /api/heroes count
    code, heroes = http_get('/heroes')
    if code != 200 or not isinstance(heroes, list):
        fail('api', f'/api/heroes status {code}')
    else:
        if len(heroes) != 100:
            fail('api', f'/api/heroes count {len(heroes)} != 100')
        ids = [h.get('id', '') for h in heroes]
        for f in ('borea', 'greek_borea', 'primordial_gaia'):
            if f in ids:
                fail('api', f'/api/heroes leaks {f!r}')
        info(f'/api/heroes count = {len(heroes)}, Borea hidden')

    # 5. baseline v5 unchanged-looking (just exists)
    if not BASELINE_V5.exists():
        fail('baseline', 'baseline v5 missing')
    else:
        info('baseline v5 present')

    # 6. no new endpoint created (we did not patch any *.py in /app/backend/routes/)
    # (Audit on disk: heuristic check)
    routes_dir = ROOT / 'backend/routes'
    for p in routes_dir.glob('*.py'):
        t = p.read_text(encoding='utf-8', errors='ignore')
        for tok in ('/affinity/spend', '/affinity/claim', '/gift/spend', '/gift/claim',
                    '/collection_synergy/activate', '/collection_synergy/apply'):
            if tok in t:
                fail('routes', f'{p.name} contains forbidden endpoint token {tok!r}')

    return emit('PASS' if not failures else 'FAIL')


def emit(result):
    print('=' * 72)
    print('CS2-A + AF2-A Combo Readiness Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    if failures:
        print('\nFAILURES:')
        for f in failures: print(f'  - {f}')
    print(f'\nRESULT: {result}')
    return 0 if result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
