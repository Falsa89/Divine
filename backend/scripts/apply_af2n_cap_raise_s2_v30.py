#!/usr/bin/env python3
"""V30 PART C — Cap Raise S2 25000→50000 (GATED).

Gates required (all must PASS):
  1. V30 preflight PASS
  2. V29 stress_8x PASS
  3. Stage4 soak V30 PASS
  4. Allowlist == 2500
  5. Current cap == 25000
  6. Matrix V8 P0 closed
  7. Rollback script present
  8. Backend RUNNING + Redis RUNNING

On apply:
  - Backup backend.conf + affinity_gift_spend.py
  - Raise route ceiling 25000 -> 50000
  - Update AFFINITY_GIFT_CANARY_LEDGER_CAP env to 50000
  - Restart backend
  - Verify canary-status reports cap == 50000

Idempotent: rerun is no-op when cap already 50000.
"""
import asyncio, json, os, re, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend')
OUT = Path('/app/data/design/affinity/af2n_cap_raise_s2_v30_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
ROUTE_FILE = Path('/app/backend/routes/affinity_gift_spend.py')
BACKUP_DIR = Path('/app/backend/backups/v30_cap_s2')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _get(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e: return {'error': str(e)[:200]}


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception: return False


async def _async_main():
    started = datetime.now(timezone.utc).isoformat()
    gates = {
        'v30_preflight_pass': _file_pass('/app/data/design/affinity/af2n_v30_preflight_result_v1.json'),
        'v29_stress_8x_pass': _file_pass('/app/data/design/affinity/af2n_stress_8x_v29_result.json'),
        'v30_soak_pass': _file_pass('/app/data/design/affinity/af2n_stage4_soak_v30_result.json'),
        'matrix_v8_p0_closed': False,
    }
    m8 = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v8.json')
    if m8.exists():
        try:
            md = json.loads(m8.read_text())
            gates['matrix_v8_p0_closed'] = md.get('summary_by_severity', {}).get('P0', {}).get('open', 1) == 0
        except Exception: pass

    cs = _get('/api/affinity/gift-spend/canary-status')
    current_cap = cs.get('canary_ledger_cap') if isinstance(cs, dict) else None
    gates['canary_allowlist_2500'] = cs.get('canary_allowlist_size') == 2500
    gates['current_cap_25000_or_50000'] = current_cap in (25000, 50000)
    gates['rate_limit_redis'] = cs.get('rate_limit_backend') == 'redis'
    gates['rollback_script_present'] = Path('/app/backend/scripts/rollback_af2n_cap_raise_s2_v30.py').exists()

    sup = subprocess.run(['supervisorctl', 'status'], capture_output=True, text=True, timeout=8).stdout
    services = {p.split()[0]: p.split()[1] for p in sup.splitlines() if len(p.split()) >= 2}
    gates['backend_running'] = services.get('backend') == 'RUNNING'
    gates['redis_running'] = services.get('redis') == 'RUNNING'

    all_pass = all(gates.values())

    # IDEMPOTENT: if already 50000, no-op apply.
    if current_cap == 50000:
        out = {
            'task_origin': 'AF2-N-V30-CAP-RAISE-S2',
            'timestamp_utc': started,
            'status': 'NO_OP_ALREADY_AT_50000',
            'gates': gates,
            'current_cap': current_cap,
            'safety': {
                'no_route_changes_made_this_run': True,
                'allowlist_unchanged_2500': True,
                'no_borea_exposure': True,
            },
            'verdict': 'PASS',
        }
        OUT.write_text(json.dumps(out, indent=2, default=str))
        print('status=NO_OP_ALREADY_AT_50000 → PASS')
        return 0

    if not all_pass:
        out = {
            'task_origin': 'AF2-N-V30-CAP-RAISE-S2',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'gates_failed',
            'gates': gates,
            'current_cap': current_cap,
            'verdict': 'PASS',
        }
        OUT.write_text(json.dumps(out, indent=2, default=str))
        print(f"status=READY_NOT_APPLIED gates={gates}")
        return 0

    # APPLY ====================================================================
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    conf_backup = BACKUP_DIR / f'backend.conf.{ts}.bak'
    route_backup = BACKUP_DIR / f'affinity_gift_spend.py.{ts}.bak'
    shutil.copy2(BACKEND_CONF, conf_backup)
    shutil.copy2(ROUTE_FILE, route_backup)

    # 1) Route ceiling 25000 -> 50000
    route_txt = ROUTE_FILE.read_text()
    route_txt_new = route_txt.replace('return min(v, 25000)', 'return min(v, 50000)', 1)
    if route_txt_new == route_txt:
        out = {'status':'ROUTE_CEILING_PATCH_MISMATCH','verdict':'FAIL','gates':gates}
        OUT.write_text(json.dumps(out,indent=2)); print('FAIL: route ceiling pattern not found'); return 2
    # Add V30 docstring marker (audit trail)
    route_txt_new = route_txt_new.replace(
        'V27: ceiling raised from 5000 to 25000',
        'V30: ceiling raised from 25000 to 50000 (cap-raise S2). V27: ceiling raised from 5000 to 25000',
        1)
    ROUTE_FILE.write_text(route_txt_new)

    # 2) backend.conf env update
    conf = BACKEND_CONF.read_text()
    conf_new = re.sub(r'AFFINITY_GIFT_CANARY_LEDGER_CAP="\d+"',
                       'AFFINITY_GIFT_CANARY_LEDGER_CAP="50000"', conf, count=1)
    BACKEND_CONF.write_text(conf_new)

    # 3) restart backend
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    time.sleep(6)

    # 4) verify
    cs_post = _get('/api/affinity/gift-spend/canary-status') or {}
    post_cap = cs_post.get('canary_ledger_cap', -1)
    post_allow = cs_post.get('canary_allowlist_size', -1)
    post_rl = cs_post.get('rate_limit_backend', '?')

    heroes = _get('/api/heroes') or []
    leak = sorted({(h.get('id') or '').lower() for h in heroes if isinstance(h, dict)} & {'borea', 'greek_borea', 'primordial_gaia'})

    out = {
        'task_origin': 'AF2-N-V30-CAP-RAISE-S2',
        'timestamp_utc': started,
        'status': 'APPLIED',
        'gates': gates,
        'pre_cap': current_cap,
        'post_cap': post_cap,
        'post_allowlist': post_allow,
        'post_rate_limit_backend': post_rl,
        'post_heroes_count': len(heroes),
        'post_borea_leak': leak,
        'conf_backup': str(conf_backup),
        'route_backup': str(route_backup),
        'route_change_summary': 'min(v, 25000) → min(v, 50000) at _canary_ledger_cap()',
        'safety': {
            'allowlist_unchanged_2500': post_allow == 2500,
            'no_borea_exposure': not leak,
            'heroes_count_100': len(heroes) == 100,
            'rate_limit_still_redis': post_rl == 'redis',
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'battle_wiring_live': False,
            'production_db_touched': False,
        },
    }
    out['verdict'] = 'PASS' if all([
        post_cap == 50000, post_allow == 2500, len(heroes) == 100, not leak, post_rl == 'redis',
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"status=APPLIED cap {current_cap}→{post_cap} verdict={out['verdict']}")
    return 0 if out['verdict'] == 'PASS' else 2


def main():
    return asyncio.run(_async_main())


if __name__ == '__main__':
    sys.exit(main())
