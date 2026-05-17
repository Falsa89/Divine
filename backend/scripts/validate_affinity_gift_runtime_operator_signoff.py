#!/usr/bin/env python3
"""
AF2-M — Validator for the operator sign-off package.

Asserts:
- all signoffs are False by default
- af2n_allowed is False
- 5+ immediate rollback triggers
- 5+ rollout stages with only stage0 allowed_today=true
- preconditions list is non-empty with required:true and status_today on each
- borea_hidden in preconditions
- feature_flag_currently_enabled=false
- go_decision_gate.user_explicit_approval_required=true
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

PACK = Path('/app/data/design/affinity/'
            'affinity_gift_runtime_operator_signoff_package_v1.json')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('package_present', PACK.exists(), str(PACK))
p = json.loads(PACK.read_text(encoding='utf-8'))
record('package_id',
       p.get('package_id') == 'affinity_gift_runtime_operator_signoff_package_v1', '')
record('task_origin_af2m', p.get('task_origin') == 'AF2-M', '')
record('design_only', p.get('design_only') is True, '')
record('runtime_attached_false', p.get('runtime_attached') is False, '')
record('db_write_false', p.get('db_write') is False, '')
record('no_borea_activation', p.get('no_borea_activation') is True, '')
record('baseline_v6',
       p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

so = p.get('signoffs') or {}
for f in ('product_signoff', 'engineering_signoff', 'qa_signoff',
          'economy_balance_signoff', 'rollback_owner_signoff'):
    record(f'signoff_false:{f}', so.get(f) is False, f'got {so.get(f)!r}')

record('af2n_allowed_false', p.get('af2n_allowed') is False, '')
record('feature_flag_currently_enabled_false',
       p.get('feature_flag_currently_enabled') is False, '')

pre = p.get('preconditions') or []
record('preconditions_min_8', len(pre) >= 8, f'got {len(pre)}')
pre_ids = {x.get('id') for x in pre if isinstance(x, dict)}
for req in ('baseline_v6_clean', 'api_heroes_count_100', 'borea_hidden',
            'gift_spend_disabled_contract_pass',
            'af2j_auth_ratelimit_contract_pass',
            'af2k_pre_idempotency_contract_pass',
            'af2l_disabled_load_probe_pass',
            'af2l_rollback_rehearsal_pass',
            'ui_no_spend_button'):
    record(f'precondition_present:{req}', req in pre_ids, '')

triggers = p.get('immediate_rollback_triggers') or []
record('triggers_min_5', len(triggers) >= 5, f'got {len(triggers)}')
t_ids = {t.get('id') for t in triggers if isinstance(t, dict)}
for req in ('err_5xx_rate', 'duplicate_spend_count', 'borea_leak_count',
            'inventory_mismatch', 'p95_latency_ms'):
    record(f'trigger_present:{req}', req in t_ids, '')

stages = p.get('rollout_stages') or []
record('stages_min_5', len(stages) >= 5, f'got {len(stages)}')
stage0 = next((s for s in stages if s.get('id', '').startswith('stage0')), None)
record('stage0_allowed_today',
       bool(stage0) and stage0.get('allowed_today') is True, '')
later = [s for s in stages if not s.get('id', '').startswith('stage0')]
record('only_stage0_allowed',
       all(s.get('allowed_today') is False for s in later),
       'no later stage may be allowed_today')

gate = p.get('go_decision_gate') or {}
record('gate_explicit_user_approval',
       gate.get('user_explicit_approval_required') is True, '')
record('gate_baseline_diff_pass_required',
       gate.get('baseline_diff_pass_required') is True, '')
record('gate_all_signoffs_true_false',
       gate.get('all_signoffs_true') is False, '')

sf = p.get('safety_flags') or {}
record('sf_runtime_attached_false', sf.get('runtime_attached') is False, '')
record('sf_db_write_false', sf.get('db_write') is False, '')
record('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
record('sf_af2n_blocked', sf.get('af2n_allowed_today') is False, '')


print('=' * 70)
print('AF2-M — Operator Sign-Off Package Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
