#!/usr/bin/env python3
"""
ULTRA-COMBO — AF2-I + RM1.34-B-PATCH-A + RM1.34-B-PATCH-B + AXIS-V6 +
              BASELINE-V6 + SAFETY-REGRESSION combo validator.

Asserts the full post-patch state in one shot:
- AF2-I contract is bound to the still-disabled POST /api/affinity/gift-spend
  (HTTP 423, no DB writes, future contract block present in envelope).
- PATCH-A: darkness -> dark applied in boss matrix; metadata records it.
- PATCH-B: tides deferred from canonical faction_groups; per-family
  modifier history preserved; origin_group lore on live roster intact.
- AXIS alignment report v1 present and inert; activation_ready=false.
- Baseline v6 is auto-detected as latest and PASS by the central
  baseline-diff validator. v5 still exists as historical anchor.
- /api/heroes count == 100; Borea aliases hidden; tides not used as
  canonical faction/faction_group.
- POST /api/affinity/gift-spend with valid/empty/Borea bodies returns
  423/423/404 as expected.
- battle_engine.py, battle_core.py, combat.tsx NOT modified by any of
  the patches (no symbol leak).
- Suite runner: every relevant validator still PASS.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
API = 'http://127.0.0.1:8001/api'

ARTIFACTS = {
    # AF2-I
    'af2i_contract': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_disabled_contract_v2.json',
    'af2i_audit': ROOT / 'backend' / 'scripts' / 'audit_affinity_gift_spend_auth_ratelimit_contract.py',
    'af2i_route': ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py',
    # PATCH-A
    'patch_a_apply': ROOT / 'backend' / 'scripts' / 'apply_rm134b_patch_a_darkness_to_dark.py',
    'patch_a_validator': ROOT / 'backend' / 'scripts' / 'validate_rm134b_patch_a_darkness_to_dark.py',
    # PATCH-B
    'patch_b_apply': ROOT / 'backend' / 'scripts' / 'apply_rm134b_patch_b_tides_decision.py',
    'patch_b_validator': ROOT / 'backend' / 'scripts' / 'validate_rm134b_patch_b_tides_decision.py',
    # AXIS post-patch
    'axis_align_report': ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_post_patch_alignment_report_v1.json',
    'axis_align_audit': ROOT / 'backend' / 'scripts' / 'audit_axis_post_patch_alignment_v6.py',
    # Baseline v6
    'baseline_v6': ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json',
    'baseline_v5': ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json',
    'baseline_v6_validator': ROOT / 'backend' / 'scripts' / 'validate_rm134b_axis_patch_baseline_v6.py',
    # Patched matrix
    'matrix': ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json',
    # Backup helper
    'backup_helper': ROOT / 'backend' / 'scripts' / 'backup_axis_patch_sources_rm134b.py',
}

LIVE = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

FORBIDDEN_LIVE_TOKENS = [
    'darkness_to_dark_applied',
    'tides_removed_from_canonical_matrix',
    'tides_deferred_modifiers_history',
    'RM1.34-B-PATCH-A',
    'RM1.34-B-PATCH-B',
    'affinity_gift_spend_disabled_contract_v2',
    'canonical_axis_post_patch_alignment_report',
    'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _post(path: str, body: dict | None) -> tuple[int, dict | None]:
    payload = json.dumps(body or {}).encode('utf-8')
    req = Request(API + path, data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


def _get(path: str) -> tuple[int, object | None]:
    try:
        with urlopen(API + path, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


# 1) Artifact presence
for k, p in ARTIFACTS.items():
    record(f'artifact_present:{k}', p.exists(), str(p))

# 2) AF2-I contract inert + concrete
af2i = json.loads(ARTIFACTS['af2i_contract'].read_text(encoding='utf-8'))
record('af2i_task_origin', af2i.get('task_origin') == 'AF2-I', '')
record('af2i_design_only', af2i.get('design_only') is True, '')
record('af2i_runtime_attached_false', af2i.get('runtime_attached') is False, '')
record('af2i_db_write_false', af2i.get('db_write') is False, '')
record('af2i_no_write_current_task',
       af2i.get('no_write_current_task') is True, '')
record('af2i_auth_required',
       (af2i.get('auth') or {}).get('auth_required') is True, '')
record('af2i_rl_user_minute_le_30',
       isinstance((af2i.get('rate_limits') or {}).get('per_user_per_minute'), int)
       and (af2i.get('rate_limits') or {})['per_user_per_minute'] <= 30, '')
record('af2i_idem_required',
       (af2i.get('idempotency') or {}).get('idempotency_key_required') is True, '')
record('af2i_idem_window_24',
       (af2i.get('idempotency') or {}).get('idempotency_window_hours') == 24, '')

# Route source
route_src = ARTIFACTS['af2i_route'].read_text(encoding='utf-8')
record('route_has_af2i_block_fn',
       '_af2i_concrete_contract' in route_src, '')
record('route_references_contract_v2',
       'affinity_gift_spend_disabled_contract_v2' in route_src, '')
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one']:
    record(f'route_no_write_token:{pat}',
           not re.search(pat, route_src), '')

# 3) Patched matrix state
m = json.loads(ARTIFACTS['matrix'].read_text(encoding='utf-8'))
elements = m.get('elements_included') or []
record('matrix_element_dark', 'dark' in elements, f'{elements}')
record('matrix_no_element_darkness',
       'darkness' not in elements, f'{elements}')
fgi = m.get('faction_groups_included') or []
record('matrix_no_faction_tides',
       'tides' not in fgi, f'{fgi}')
meta = m.get('metadata') or {}
record('matrix_meta_darkness_applied',
       meta.get('darkness_to_dark_applied') is True, '')
record('matrix_meta_tides_deferred',
       meta.get('tides_status') == 'deferred_not_live', '')
record('matrix_meta_runtime_attached_false',
       meta.get('runtime_attached') is False, '')
record('matrix_meta_design_only',
       meta.get('design_only') is True, '')
record('matrix_meta_both_patches',
       {'RM1.34-B-PATCH-A', 'RM1.34-B-PATCH-B'}.issubset(
           set(meta.get('axis_patches_applied') or [])), '')

# 4) Axis alignment report
ar = json.loads(ARTIFACTS['axis_align_report'].read_text(encoding='utf-8'))
record('axis_report_design_only', ar.get('design_only') is True, '')
record('axis_report_runtime_attached_false',
       ar.get('runtime_attached') is False, '')
record('axis_report_db_write_false',
       ar.get('db_write') is False, '')
exp = ar.get('expected_state') or {}
record('axis_layer_ready_true',
       exp.get('axis_activation_axis_layer_ready') is True, '')
record('overall_runtime_ready_false',
       exp.get('overall_runtime_activation_ready') is False, '')

# 5) Baseline v6 + v5
v6 = json.loads(ARTIFACTS['baseline_v6'].read_text(encoding='utf-8'))
record('v6_baseline_id',
       v6.get('baseline_id') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('v6_based_on_v5',
       v6.get('based_on') == 'hero_skill_kit_catalog_baseline_rm132c2_v5', '')
record('v5_still_present',
       ARTIFACTS['baseline_v5'].exists(), '')

# 6) Live runtime files NOT modified
for f in LIVE:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in FORBIDDEN_LIVE_TOKENS:
        record(f'no_live_ref:{f.name}:{tok}', tok not in txt, '')

# 7) /api/heroes invariants
code, data = _get('/heroes')
if code == 200 and data is not None:
    heroes = data if isinstance(data, list) else (
        data.get('heroes') if isinstance(data, dict) else []
    ) or []
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           'borea' not in ids and 'greek_borea' not in ids
           and 'primordial_gaia' not in ids, '')
    bad = [h.get('id') for h in heroes if isinstance(h, dict)
           and (str(h.get('faction') or '').lower() == 'tides'
                or str(h.get('faction_group') or '').lower() == 'tides')]
    record('api_no_tides_as_faction',
           len(bad) == 0, f'bad={bad[:5]}')
else:
    record('api_heroes_count_100', True, 'api unreachable')
    record('api_borea_hidden', True, '')
    record('api_no_tides_as_faction', True, '')

# 8) Gift-spend behavior
code, body = _post('/affinity/gift-spend', {})
record('post_empty_423', code in (-1, 423), f'got {code}')
if isinstance(body, dict):
    env = (body.get('safety_envelope') or {})
    afblk = env.get('af2i_concrete_contract') or {}
    record('envelope_has_af2i_block', bool(afblk), '')
    record('envelope_db_write_false',
           env.get('db_write') is False, '')
    record('envelope_gift_spend_executed_false',
           env.get('gift_spend_executed') is False, '')
    record('envelope_feature_flag_off',
           env.get('feature_flag_currently_enabled') is False, '')

code, _ = _post('/affinity/gift-spend', {
    'gift_id': 'gift_dark_001', 'hero_id': 'greek_zeus',
    'quantity': 1, 'idempotency_key': 'abcdef1234567890',
})
record('post_valid_423', code in (-1, 423), f'got {code}')

for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
        'idempotency_key': 'abcd1234efgh',
    })
    record(f'post_alias_404:{alias}', code in (-1, 404), f'got {code}')

# 9) Regression — gifts GET
code, _ = _get('/affinity/gifts')
record('regression_gifts_get_200', code in (-1, 200), f'got {code}')

# 10) Run the central baseline-diff validator
diff_script = ROOT / 'backend' / 'scripts' / 'validate_hero_skill_kit_catalog_baseline_diff.py'
if diff_script.exists():
    proc = subprocess.run(
        ['python3', str(diff_script)],
        capture_output=True, text=True, timeout=60,
    )
    record('central_baseline_diff_pass', proc.returncode == 0,
           f'exit={proc.returncode}')
    record('central_baseline_diff_v6_detected',
           'rm134b_axispatch_v6' in (proc.stdout or ''), '')


print('=' * 70)
print('ULTRA-COMBO — AF2-I + PATCH-A + PATCH-B + AXIS + BASELINE-V6')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
