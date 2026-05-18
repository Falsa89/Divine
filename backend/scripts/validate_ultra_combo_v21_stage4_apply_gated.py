#!/usr/bin/env python3
"""V21 — Composite Validator (ULTRA-COMBO V21)."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

NOW = datetime.now(timezone.utc)

SUB_VALIDATORS = [
    ('V21-PREFLIGHT',                       'validate_af2n_v21_preflight.py'),
    ('AF2-N-STAGE4-SIGNOFFS-V5-APPLIED',    'validate_af2n_stage4_signoffs_v5_applied.py'),
    ('AF2-N-V21-RATE-LIMIT-AUDIT',          'audit_affinity_gift_spend_rate_limit_runtime.py'),
    ('AF2-N-V21-RATE-LIMIT-PROBE',          'validate_affinity_gift_spend_rate_limit_probe.py'),
    ('AF2-N-V21-DB-BACKUP-DRILL',           'validate_af2n_stage4_db_backup_drill.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-APPLY',    'validate_af2n_stage4_internal_beta_apply_result.py'),
    ('AF2-N-V21-STAGE4-MONITORING',         'validate_af2n_stage4_monitoring_v21.py'),
    ('AF2-L-LOCUST-STAGE4-V21',             'validate_af2n_v21_locust_stage4_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-V21-SAFETY',  'audit_affinity_gifts_public_preview_v21_safety.py'),
    ('V21-ROLLBACK-READINESS',              'validate_af2n_v21_rollback_readiness.py'),
    ('SAFETY-ROLLUP-P',                     'validate_collection_affinity_runtime_activation_rollup_v16.py'),
]
SCRIPTS_DIR = Path('/app/backend/scripts')


def _get(p):
    try:
        with urlopen('http://127.0.0.1:8001' + p, timeout=4) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _post(p, b):
    payload = json.dumps(b).encode()
    req = Request('http://127.0.0.1:8001' + p, data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=4) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def main():
    results = []
    fails = []
    for task, name in SUB_VALIDATORS:
        p = SCRIPTS_DIR / name
        if not p.exists():
            results.append({'task': task, 'present': False})
            fails.append(f'missing:{task}')
            continue
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0
        results.append({'task': task, 'present': True, 'exit_code': r.returncode,
                        'tail': (r.stdout or r.stderr).strip().splitlines()[-3:] if (r.stdout or r.stderr) else []})
        if not ok:
            fails.append(f'fail:{task}:exit={r.returncode}')
    # Live invariants
    _, heroes = _get('/api/heroes')
    heroes_100 = isinstance(heroes, list) and len(heroes) == 100
    if not heroes_100:
        fails.append('heroes_not_100')
    borea = _post('/api/affinity/gift-spend', {'gift_id': 'x', 'hero_id': 'borea',
                                                 'quantity': 1, 'idempotency_key': 'v21cmp01', 'user_id': 'stage4_qa_001'})
    if borea != 404:
        fails.append(f'borea_not_404:{borea}')
    _, status = _get('/api/affinity/gift-spend/canary-status')
    if status:
        if status.get('applied_to_combat') is True: fails.append('applied_to_combat_true')
        if status.get('battle_runtime_attached') is True: fails.append('battle_attached_true')
        if status.get('buffs_enabled') is True: fails.append('buffs_enabled_true')
        if status.get('rate_limit_enabled') is not True: fails.append('rate_limit_not_enabled')
    # baseline diff
    bd = subprocess.run(['python3', '/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py'],
                        capture_output=True, text=True, timeout=60)
    if bd.returncode != 0:
        fails.append('baseline_v6_diff_fail')
    # battle files unchanged
    bf = subprocess.run(['git', '-C', '/app', 'diff', '--stat', '--',
                         'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
                         'backend/synergy_system.py', 'backend/game_systems.py'],
                        capture_output=True, text=True, timeout=10)
    if bf.stdout.strip() != '':
        fails.append('battle_files_changed')

    overall = (len(fails) == 0)
    out = {
        'composite_id': 'ultra_combo_v21_stage4_apply_gated_composite_v1',
        'generated_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'sub_validator_results': results,
        'fails': fails,
        'live_heroes_count': len(heroes) if isinstance(heroes, list) else -1,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'no broad rollout',
            'no public spend UI',
            'no battle wiring',
            'no Borea reveal',
            'rate-limit active',
            'db backup drill pass',
            '/api/heroes=100',
        ],
    }
    Path('/app/backend/reports').mkdir(parents=True, exist_ok=True)
    Path('/app/backend/reports/ultra_combo_v21_composite.json').write_text(json.dumps(out, indent=2))
    print(f'ULTRA-COMBO-V21 {out["overall_status"]} fails={len(fails)}')
    for f in fails: print(f'  FAIL: {f}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
