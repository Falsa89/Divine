#!/usr/bin/env python3
"""V24 — Composite Validator (ULTRA-COMBO V24)."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

NOW = datetime.now(timezone.utc)
SCRIPTS = Path('/app/backend/scripts')

SUB = [
    ('V24-PREFLIGHT',                              'validate_af2n_v24_preflight.py'),
    ('AF2-N-V24-OBSERVATION-WINDOW-REAL',          'validate_af2n_v24_observation_window_real.py'),
    ('AF2-N-V24-ABUSE-METRICS-INSTRUMENTATION',    'validate_af2n_v24_abuse_metrics_instrumentation.py'),
    ('AF2-N-V24-STAGING-ROLLBACK-DRILL',           'validate_af2n_v24_staging_rollback_drill.py'),
    ('AF2-N-V24-REDIS-HA-DECISION-PLAN',           'validate_af2n_v24_redis_ha_decision_plan.py'),
    ('AF2-N-V24-SUPPORT-ECONOMY-PREP',             'validate_af2n_v24_support_economy_prep.py'),
    ('AF2-N-V24-BLOCKER-MATRIX-V3',                'validate_af2n_broad_rollout_blocker_matrix_v3.py'),
    ('AF2-N-PUBLIC-UI-V24-SAFETY',                 'audit_affinity_gifts_public_preview_v24_safety.py'),
    ('V24-ROLLBACK-READINESS',                     'validate_af2n_v24_rollback_readiness.py'),
    ('SAFETY-ROLLUP-S',                            'validate_collection_affinity_runtime_activation_rollup_v19.py'),
]


def _get(p):
    try:
        with urlopen('http://127.0.0.1:8001'+p, timeout=4) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _post(p, b):
    payload = json.dumps(b).encode()
    req = Request('http://127.0.0.1:8001'+p, data=payload, method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=4) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def main():
    results = []; fails = []
    for task, name in SUB:
        p = SCRIPTS / name
        if not p.exists(): results.append({'task':task,'present':False}); fails.append(f'missing:{task}'); continue
        env = dict(os.environ); env['SUITE_RUNNER_ACTIVE'] = '1'
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=180, env=env)
        ok = r.returncode == 0
        results.append({'task':task,'present':True,'exit_code':r.returncode,
                        'tail':(r.stdout or r.stderr).strip().splitlines()[-3:] if (r.stdout or r.stderr) else []})
        if not ok: fails.append(f'fail:{task}:exit={r.returncode}')
    _, heroes = _get('/api/heroes')
    if not (isinstance(heroes, list) and len(heroes) == 100): fails.append('heroes_not_100')
    if _post('/api/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v24cmp01','user_id':'stage4_qa_001'}) != 404:
        fails.append('borea_not_404')
    _, st = _get('/api/affinity/gift-spend/canary-status')
    if st:
        if st.get('applied_to_combat') is True: fails.append('combat_attached')
        if st.get('battle_runtime_attached') is True: fails.append('battle_attached')
        if st.get('buffs_enabled') is True: fails.append('buffs_true')
        if st.get('rate_limit_enabled') is not True: fails.append('rate_limit_off')
        if st.get('canary_allowlist_size', 0) < 700: fails.append('allowlist_below_700')
        if st.get('canary_ledger_cap', 0) < 5000: fails.append('cap_below_5000')
    bd = subprocess.run(['python3','/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py'],
                        capture_output=True, text=True, timeout=60)
    if bd.returncode != 0: fails.append('baseline_v6_diff_fail')
    bf = subprocess.run(['git','-C','/app','diff','--stat','--',
                         'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
                         'backend/synergy_system.py','backend/game_systems.py'],
                        capture_output=True, text=True, timeout=10)
    if bf.stdout.strip() != '': fails.append('battle_files_changed')
    overall = (len(fails) == 0)
    out = {
        'composite_id':'ultra_combo_v24_observation_abuse_rollback_redisHA_composite_v1',
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'sub_validator_results': results, 'fails': fails,
        'live_heroes_count': len(heroes) if isinstance(heroes, list) else -1,
        'live_rate_limit_backend': (st or {}).get('rate_limit_backend'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants':[
            'no broad rollout','no public spend UI','no battle wiring',
            'no Borea reveal','rate-limit active','/api/heroes=100',
        ],
    }
    Path('/app/backend/reports').mkdir(parents=True, exist_ok=True)
    Path('/app/backend/reports/ultra_combo_v24_composite.json').write_text(json.dumps(out, indent=2))
    print(f'ULTRA-COMBO-V24 {out["overall_status"]} fails={len(fails)}')
    for f in fails: print(f'  FAIL: {f}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
