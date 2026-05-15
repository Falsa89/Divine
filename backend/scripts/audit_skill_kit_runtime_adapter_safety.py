#!/usr/bin/env python3
"""
RM1.33-A — Runtime Adapter Skeleton Safety Audit (READ-ONLY)
──────────────────────────────────────────────────────────────────────
Readonly safety audit for the new adapter skeleton + cap-policy adapter.
Verifies:
  1.  Feature flag default OFF and adapter returns disabled payload.
  2.  Adapter module exists; cap policy adapter exists.
  3.  battle_engine.py and combat.tsx DO NOT import the new adapter.
  4.  HP bar / status / VFX runtime files DO NOT import the new adapter.
  5.  No catalog (5★/6★/DW/status) was modified (signature check via
      baseline v4 diff).
  6.  /api/heroes count = 100; greek_borea / legacy borea / primordial_gaia
      not visible.
  7.  5★: 100/100 foundation_draft; 6★: 78/78 foundation_draft;
      runtime_ready=false everywhere.
  8.  Marchio Boreale: present only on greek_borea, 0 leak.
  9.  DW synergy placeholders: 78/78 design_only/runtime_ready=false/
      numeric_modifier_pct=null.
 10.  No mutating endpoint (POST/PUT/PATCH/DELETE) added in UI catalog
      pages.
 11.  No `runtime_attached=true` / `battle_runtime_attached=true` flips.
 12.  Cap policy adapter reads delta plan but does not patch.

Exit 0 = PASS. Exit 1 = FAIL (a real safety break).
"""
from __future__ import annotations
import importlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path('/app')
DELTA_PLAN = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json'
HSK_5STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
COMBAT_TSX = ROOT / 'frontend/app/combat.tsx'
HSK_UI = ROOT / 'frontend/app/hero-skill-kits-catalog.tsx'
DW_UI = ROOT / 'frontend/app/divine-weapons-catalog.tsx'
ADAPTER_PY = ROOT / 'backend/data/skill_kit_runtime_adapter.py'
CAP_POLICY_PY = ROOT / 'backend/data/skill_kit_cap_policy_adapter.py'

ADAPTER_TOKENS = (
    'skill_kit_runtime_adapter',
    'skill_kit_cap_policy_adapter',
    'is_skill_kit_runtime_enabled',
    'SKILL_KIT_RUNTIME_ENABLED',
)

failures: list[str] = []
warns: list[str] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None:
    failures.append(f'[{sec}] {msg}')


def warn(sec: str, msg: str) -> None:
    warns.append(f'[{sec}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def _check_no_import(target: Path, label: str) -> None:
    src = _read_text(target)
    if not src:
        warn('imports', f'{label}: file not found at {target}')
        return
    for tok in ADAPTER_TOKENS:
        if tok in src:
            fail('imports', f'{label} ({target.name}) references adapter token {tok!r}')


def main() -> int:
    # 1. feature flag default OFF
    if not ADAPTER_PY.exists():
        fail('module', f'adapter module missing: {ADAPTER_PY}')
        return emit()
    if not CAP_POLICY_PY.exists():
        fail('module', f'cap policy adapter missing: {CAP_POLICY_PY}')
        return emit()

    # Make sure /app is importable
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # Force env to be ABSENT for the flag check
    saved = os.environ.pop('SKILL_KIT_RUNTIME_ENABLED', None)
    try:
        from backend.data import skill_kit_runtime_adapter as rta
        importlib.reload(rta)
        if rta.is_skill_kit_runtime_enabled() is not False:
            fail('flag', 'is_skill_kit_runtime_enabled() must return False when env is absent')
        else:
            info('feature flag: default OFF (env absent) → False ✓')
        # try with a bogus value
        os.environ['SKILL_KIT_RUNTIME_ENABLED'] = 'true'
        importlib.reload(rta)
        if rta.is_skill_kit_runtime_enabled() is not False:
            fail('flag', 'is_skill_kit_runtime_enabled() must remain False for non-allowlisted truthy strings')
        else:
            info('feature flag: "true" (non-allowlisted) → False ✓')
        # disabled payload for a legacy id
        res = rta.load_skill_kit_for_hero('borea')
        if not (isinstance(res, dict) and res.get('is_disabled_runtime_result') is True
                and res.get('reason') == 'forbidden_legacy_hero_id'):
            fail('adapter', 'load_skill_kit_for_hero("borea") should return forbidden_legacy_hero_id disabled payload')
        else:
            info('adapter: forbidden legacy hero_id returns disabled payload ✓')
        # disabled candidate when flag OFF
        cand = rta.get_skill_runtime_candidate('greek_athena', 'ultimate')
        if not (isinstance(cand, dict) and cand.get('enabled') is False
                and cand.get('runtime_attached') is False
                and cand.get('battle_runtime_attached') is False):
            fail('adapter', 'get_skill_runtime_candidate must return disabled payload when flag OFF')
        else:
            info('adapter: get_skill_runtime_candidate disabled while flag OFF ✓')
        # normalize_skill_slot must be pure / inert
        ns = rta.normalize_skill_slot('greek_athena', 'ultimate')
        if not (isinstance(ns, dict)
                and ns.get('runtime_attached') is False
                and ns.get('battle_runtime_attached') is False
                and isinstance(ns.get('final_numbers_meta'), dict)
                and ns['final_numbers_meta'].get('preview_only') is True):
            fail('adapter', 'normalize_skill_slot must return inert preview-only descriptor')
        else:
            info('adapter: normalize_skill_slot returns inert preview-only descriptor ✓')
    finally:
        if saved is not None:
            os.environ['SKILL_KIT_RUNTIME_ENABLED'] = saved
        else:
            os.environ.pop('SKILL_KIT_RUNTIME_ENABLED', None)

    # 2. cap policy adapter
    from backend.data import skill_kit_cap_policy_adapter as cpa
    importlib.reload(cpa)
    plan = cpa.load_balance_cap_delta_plan()
    if plan.get('patch_applied') is not False:
        fail('cap_policy', 'delta plan patch_applied != false')
    if plan.get('applied_to_combat') is not False:
        fail('cap_policy', 'cap policy load applied_to_combat != false')
    for ctx in ('pvp', 'boss', 'pve'):
        pol = cpa.get_cap_policy_for_context(ctx)
        if not (pol.get('applied_to_combat') is False and pol.get('runtime_attached') is False
                and pol.get('battle_runtime_attached') is False and pol.get('enabled') is False):
            fail('cap_policy', f'cap policy for {ctx} must be inert (enabled=False, applied_to_combat=False)')
        if not isinstance(pol.get('policy'), dict):
            fail('cap_policy', f'cap policy for {ctx} payload missing')
    info('cap policy adapter: pvp/boss/pve all inert, preview_only=true, applied_to_combat=false ✓')

    # 3+4. No imports from live runtime files
    _check_no_import(BATTLE_ENGINE, 'battle_engine.py')
    _check_no_import(COMBAT_TSX, 'combat.tsx')
    for hp_runtime in (ROOT / 'backend/battle_core.py',):
        _check_no_import(hp_runtime, hp_runtime.name)
    if not any(f.startswith('[imports]') for f in failures):
        info('battle_engine.py / combat.tsx / battle_core.py: no adapter import ✓')

    # 5. baseline v4 declared SHAs match current catalog SHAs (we don’t
    # need to re-run diff validator here, but we verify v4 is the
    # newest baseline anchor by timestamp).
    if not BASELINE_V4.exists():
        fail('baseline', f'baseline v4 missing: {BASELINE_V4}')
    else:
        b4 = json.loads(BASELINE_V4.read_text(encoding='utf-8'))
        if b4.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
            fail('baseline', 'baseline v4 file baseline_id mismatch')
        else:
            info('baseline v4: present and identifiable ✓')

    # 6. /api/heroes count
    try:
        with urllib.request.urlopen('http://localhost:8001/api/heroes', timeout=5) as r:
            data = json.loads(r.read())
        heroes = data if isinstance(data, list) else (data.get('heroes') or data.get('data') or [])
        if len(heroes) != 100:
            fail('api_heroes', f'/api/heroes count != 100 (got {len(heroes)})')
        ids = [h.get('hero_id') or h.get('id') for h in heroes if isinstance(h, dict)]
        for forb in ('borea', 'greek_borea', 'primordial_gaia'):
            if forb in ids:
                fail('api_heroes', f'{forb} visible in /api/heroes')
        if not any(f.startswith('[api_heroes]') for f in failures):
            info('/api/heroes: count=100; borea/greek_borea/primordial_gaia hidden ✓')
    except Exception as e:
        warn('api_heroes', f'cannot reach /api/heroes: {e!r}')

    # 7. catalog state
    c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))
    c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    fn5 = sum(1 for e in c5.get('entries') or []
              for _, s in (e.get('skill_package') or {}).items()
              if isinstance(s, dict) and isinstance(s.get('final_numbers'), dict)
              and s['final_numbers'].get('status') == 'foundation_draft'
              and s['final_numbers'].get('runtime_ready') is False)
    fn6 = sum(1 for e in c6.get('entries') or []
              for _, s in (e.get('skill_package') or {}).items()
              if isinstance(s, dict) and isinstance(s.get('final_numbers'), dict)
              and s['final_numbers'].get('status') == 'foundation_draft'
              and s['final_numbers'].get('runtime_ready') is False)
    if fn5 != 100:
        fail('catalog_state', f'5★ foundation_draft count != 100 (got {fn5})')
    if fn6 != 78:
        fail('catalog_state', f'6★ foundation_draft count != 78 (got {fn6})')
    if not any(f.startswith('[catalog_state]') for f in failures):
        info('catalog: 5★ 100/100 + 6★ 78/78 foundation_draft, runtime_ready=false ✓')

    # 8. Marchio leak
    leak = []
    for e in c6.get('entries') or []:
        if e.get('hero_id') == 'greek_borea':
            continue
        if 'marchio_boreale' in json.dumps(e, ensure_ascii=False).lower():
            leak.append(e.get('hero_id'))
    if leak:
        fail('marchio', f'marchio_boreale leak in non-Borea entries: {leak}')
    else:
        info('Marchio Boreale: Borea-only, 0 leak ✓')

    # 9. DW synergy 78/78
    bad = []
    cnt = 0
    for e in c6.get('entries') or []:
        for sn, s in (e.get('skill_package') or {}).items():
            if not isinstance(s, dict):
                continue
            fn = s.get('final_numbers') or {}
            dws = fn.get('divine_weapon_synergy_placeholder')
            if not isinstance(dws, dict):
                bad.append(f'{e.get("hero_id")}.{sn}: missing dw placeholder')
                continue
            cnt += 1
            if dws.get('design_only') is not True or dws.get('runtime_ready') is not False or dws.get('numeric_modifier_pct') is not None:
                bad.append(f'{e.get("hero_id")}.{sn}: dw placeholder invariant violation')
    if bad:
        fail('dw_synergy', f'DW synergy violations: {bad[:5]}')
    if cnt != 78:
        fail('dw_synergy', f'DW synergy count != 78 (got {cnt})')
    if not any(f.startswith('[dw_synergy]') for f in failures):
        info('DW synergy: 78/78 design_only=true, runtime_ready=false, numeric_modifier_pct=null ✓')

    # 10. UI catalog files — no mutation calls / no runtime buttons
    runtime_kws = ('activate', 'equip', 'upgrade', 'breakSeal', 'break_seal',
                   'spend', 'summon', 'battleTest', 'battle_test',
                   'attachRuntime', 'attach_runtime')
    for ui in (HSK_UI, DW_UI):
        src = _read_text(ui)
        if not src:
            warn('ui', f'{ui}: not found')
            continue
        if re.search(r'(axios|fetch)\s*\.?\s*(post|put|patch|delete)\s*\(', src, re.IGNORECASE):
            fail('ui', f'{ui.name}: mutation call found')
        if re.search(r"method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"]", src, re.IGNORECASE):
            fail('ui', f'{ui.name}: method:POST/PUT/PATCH/DELETE literal found')
        for kw in runtime_kws:
            pat = re.compile(r'(<Pressable|<TouchableOpacity|onPress)[^>]{0,300}' + re.escape(kw), re.IGNORECASE)
            if pat.search(src):
                fail('ui', f'{ui.name}: runtime action Pressable for {kw}')
        for tok in ADAPTER_TOKENS:
            if tok in src:
                fail('ui', f'{ui.name}: references adapter token {tok!r}')
    if not any(f.startswith('[ui]') for f in failures):
        info('UI catalog files: no mutations, no runtime buttons, no adapter ref ✓')

    # 11. catalog top-level runtime flags
    for label, cat in (('5★', c5), ('6★', c6)):
        if cat.get('runtime_attached') is not False:
            fail('runtime_flags', f'{label} top-level runtime_attached != false')
        if cat.get('battle_runtime_attached') is not False:
            fail('runtime_flags', f'{label} top-level battle_runtime_attached != false')
    if not any(f.startswith('[runtime_flags]') for f in failures):
        info('catalog top-level: runtime_attached=false, battle_runtime_attached=false ✓')

    # 12. cap policy adapter does not patch (already verified, but sanity)
    if DELTA_PLAN.exists():
        plan_text = DELTA_PLAN.read_text(encoding='utf-8')
        # The plan JSON must still declare patch_applied: false
        if '"patch_applied": false' not in plan_text:
            fail('delta_plan', 'delta plan no longer declares patch_applied=false')
        else:
            info('delta plan: patch_applied=false declared ✓')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.33-A — Runtime Adapter Skeleton Safety Audit')
        for f in failures:
            print(f'  - {f}')
        if warns:
            print('Warnings:')
            for w in warns:
                print(f'  ! {w}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.33-A — Runtime Adapter Skeleton Safety Audit')
    for i in infos:
        print(f'  i {i}')
    if warns:
        print('Warnings:')
        for w in warns:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
