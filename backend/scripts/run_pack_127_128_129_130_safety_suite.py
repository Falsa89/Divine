#!/usr/bin/env python3
"""Pack 127 + 128 + 129 + 130 Safety Suite Runner."""
from __future__ import annotations
import json, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / 'backend' / 'scripts'
REPORTS = REPO_ROOT / 'backend' / 'reports'
REPORTS.mkdir(parents=True, exist_ok=True)

PACK_127 = [f'validate_pack_127_{n}.py' for n in ['pre_qa_env_preflight', 'backend_no_startup_writes',
    'bot_system_disabled', 'battle_simulate_fail_closed', 'backend_mutation_allowlist',
    'no_mutating_get', 'borea_hidden_runtime_invariant', 'stale_ready_pass_declassification']]
PACK_128 = [f'validate_pack_128_{n}.py' for n in ['route_allowlist_registry', 'deeplink_lockdown',
    'frontend_forbidden_route_reachability', 'backend_mutation_middleware_runtime',
    'backend_mutation_allowlist_enforcement', 'mutating_get_hardening',
    'battle_simulate_runtime_block', 'no_pack129_130_131_leak', 'forbidden_areas_untouched']]
PACK_129 = [f'validate_pack_129_{n}.py' for n in ['server_ready_guard', 'teamformation_server_scope',
    'team_save_validation', 'team_save_no_rewards_no_progress', 'structured_errors_contract',
    'frontend_structured_error_mapping', 'mutation_guard_team_allowlist_interaction',
    'no_account_wide_team_fallback', 'no_pack130_131_132_133_leak', 'forbidden_areas_untouched']]
PACK_130 = [f'validate_pack_130_{n}.py' for n in ['lobby_launch_context_contract',
    'real_player_snapshot_server_scope', 'launch_context_no_db_writes',
    'snapshot_no_client_trust', 'launch_context_structured_errors',
    'pack128_mutation_guard_interaction', 'frontend_lobby_integration_safe',
    'no_combat_consumes_snapshot', 'no_rewards_no_progress',
    'no_pack131_132_133_leak', 'forbidden_areas_untouched']]


def backend_up():
    try:
        s = socket.create_connection(('127.0.0.1', 8001), timeout=1.5); s.close(); return True
    except Exception: return False


def run_one(script):
    path = SCRIPTS / script
    if not path.exists(): return {'name': script, 'status': 'MISSING', 'rc': -1, 'duration_s': 0.0, 'stdout_tail': '', 'stderr_tail': ''}
    t0 = time.time()
    r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=90)
    return {'name': script, 'status': 'PASS' if r.returncode == 0 else 'FAIL', 'rc': r.returncode,
            'duration_s': round(time.time() - t0, 3),
            'stdout_tail': '\n'.join(r.stdout.splitlines()[-6:]),
            'stderr_tail': '\n'.join(r.stderr.splitlines()[-3:]) if r.stderr else ''}


def main():
    up = backend_up()
    print(f'Backend liveness: {"UP" if up else "DOWN"}'); print('=' * 72)
    results = []
    for gname, scripts in [('PACK 127', PACK_127), ('PACK 128', PACK_128), ('PACK 129', PACK_129), ('PACK 130', PACK_130)]:
        print(f'\n--- {gname} ---')
        for s in scripts:
            res = run_one(s); results.append(res)
            print(f'  {res["status"]:6s} rc={res["rc"]} {res["duration_s"]}s  {s}')
            if res['status'] == 'FAIL':
                print(f'    stdout: {res["stdout_tail"][:300]}')
                if res['stderr_tail']: print(f'    stderr: {res["stderr_tail"][:200]}')
    fails = [r for r in results if r['status'] == 'FAIL']
    print('\n' + '=' * 72)
    print(f'TOTAL: {len(results)} | PASS: {len(results)-len(fails)} | FAIL: {len(fails)}')
    suite_status = 'PASS' if not fails else 'FAIL'
    suite_report = {'suite': 'PACK_127_128_129_130_SAFETY_SUITE', 'status': suite_status, 'backend_up': up,
                    'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'results': results}
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (REPORTS / f'pack_127_128_129_130_safety_suite_{ts}.json').write_text(json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    (REPORTS / 'pack_127_128_129_130_safety_suite_latest.json').write_text(json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Suite status: {suite_status}')
    return 0 if suite_status == 'PASS' else 1


if __name__ == '__main__': sys.exit(main())
