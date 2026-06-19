#!/usr/bin/env python3
"""Pack 127 + 128 + 129 Safety Suite Runner.

Esegue in sequenza tutti i validator Pack 127, 128 e 129 e produce un report
machine-readable. Mantiene tutti i controlli precedenti (no validator
indebolito, no test rimosso).
"""
from __future__ import annotations
import json, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / 'backend' / 'scripts'
REPORTS = REPO_ROOT / 'backend' / 'reports'
REPORTS.mkdir(parents=True, exist_ok=True)

PACK_127 = [
    'validate_pack_127_pre_qa_env_preflight.py',
    'validate_pack_127_backend_no_startup_writes.py',
    'validate_pack_127_bot_system_disabled.py',
    'validate_pack_127_battle_simulate_fail_closed.py',
    'validate_pack_127_backend_mutation_allowlist.py',
    'validate_pack_127_no_mutating_get.py',
    'validate_pack_127_borea_hidden_runtime_invariant.py',
    'validate_pack_127_stale_ready_pass_declassification.py',
]
PACK_128 = [
    'validate_pack_128_route_allowlist_registry.py',
    'validate_pack_128_deeplink_lockdown.py',
    'validate_pack_128_frontend_forbidden_route_reachability.py',
    'validate_pack_128_backend_mutation_middleware_runtime.py',
    'validate_pack_128_backend_mutation_allowlist_enforcement.py',
    'validate_pack_128_mutating_get_hardening.py',
    'validate_pack_128_battle_simulate_runtime_block.py',
    'validate_pack_128_no_pack129_130_131_leak.py',
    'validate_pack_128_forbidden_areas_untouched.py',
]
PACK_129 = [
    'validate_pack_129_server_ready_guard.py',
    'validate_pack_129_teamformation_server_scope.py',
    'validate_pack_129_team_save_validation.py',
    'validate_pack_129_team_save_no_rewards_no_progress.py',
    'validate_pack_129_structured_errors_contract.py',
    'validate_pack_129_frontend_structured_error_mapping.py',
    'validate_pack_129_mutation_guard_team_allowlist_interaction.py',
    'validate_pack_129_no_account_wide_team_fallback.py',
    'validate_pack_129_no_pack130_131_132_133_leak.py',
    'validate_pack_129_forbidden_areas_untouched.py',
]


def backend_up() -> bool:
    try:
        s = socket.create_connection(('127.0.0.1', 8001), timeout=1.5); s.close(); return True
    except Exception:
        return False


def run_one(script: str) -> dict:
    path = SCRIPTS / script
    if not path.exists():
        return {'name': script, 'status': 'MISSING', 'rc': -1, 'duration_s': 0.0, 'stdout_tail': '', 'stderr_tail': ''}
    t0 = time.time()
    r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=90)
    dur = round(time.time() - t0, 3)
    rc = r.returncode
    return {
        'name': script,
        'status': 'PASS' if rc == 0 else 'FAIL',
        'rc': rc,
        'duration_s': dur,
        'stdout_tail': '\n'.join(r.stdout.splitlines()[-6:]),
        'stderr_tail': '\n'.join(r.stderr.splitlines()[-3:]) if r.stderr else '',
    }


def main() -> int:
    up = backend_up()
    print(f'Backend liveness: {"UP" if up else "DOWN"}')
    print('=' * 72)
    results = []
    for group_name, scripts in [('PACK 127', PACK_127), ('PACK 128', PACK_128), ('PACK 129', PACK_129)]:
        print(f'\n--- {group_name} ---')
        for s in scripts:
            res = run_one(s)
            print(f'  {res["status"]:6s} rc={res["rc"]} {res["duration_s"]}s  {s}')
            if res['status'] == 'FAIL':
                print(f'    stdout: {res["stdout_tail"][:300]}')
                if res['stderr_tail']: print(f'    stderr: {res["stderr_tail"][:200]}')
            results.append(res)
    fails = [r for r in results if r['status'] == 'FAIL']
    print('\n' + '=' * 72)
    print(f'TOTAL: {len(results)} | PASS: {len(results)-len(fails)} | FAIL: {len(fails)}')
    suite_status = 'PASS' if not fails else 'FAIL'
    suite_report = {
        'suite': 'PACK_127_128_129_SAFETY_SUITE',
        'status': suite_status, 'backend_up': up,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'results': results,
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f'pack_127_128_129_safety_suite_{ts}.json'
    latest = REPORTS / 'pack_127_128_129_safety_suite_latest.json'
    out.write_text(json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    latest.write_text(json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Suite report: {out.name}')
    print(f'Suite status: {suite_status}')
    return 0 if suite_status == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
