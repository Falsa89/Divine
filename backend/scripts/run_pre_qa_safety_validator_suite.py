#!/usr/bin/env python3
"""Pre-QA Safety Validator Suite (Pack 115F).

Suite focalizzata sulla VERITA' di sicurezza pre-QA. Esegue effettivamente
gli script figli (validator/smoke/rollup) per i Pack 113, 114, 114B, 115A,
115B, 115C, 115D, 115E e il nuovo Pack 115F.

Output:
  - JSON machine-readable in `backend/reports/pre_qa_safety_validator_suite_<UTC>.json`
    contenente per ogni voce: name, kind, command, returncode, status, reason,
    duration_s, stdout_tail, stderr_tail.
  - Riassunto human-readable su stdout.

Stati possibili (verita', mai falso PASS):
  - PASS                       : il figlio e' uscito con returncode == 0.
  - FAIL                       : il figlio e' uscito con returncode != 0
                                 e NON ha motivo legittimo di skip.
  - SKIPPED_BACKEND_DOWN       : smoke runtime che richiede backend ma backend
                                 e' irraggiungibile.
  - SKIPPED_REASON_EXPLICIT    : skip esplicito con motivazione (es. script
                                 figlio mancante, classificato come opzionale).

Exit code del runner:
  - 0 se: 0 FAIL e tutti gli skip sono classificati esplicitamente.
  - 1 se: almeno un FAIL (anche solo uno) — la suite e' truthful.

Non modifica DB. Non attiva feature. Non e' interattivo.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ------------------------------------------------------------
# Path setup
# ------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(R, 'backend', 'scripts')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ------------------------------------------------------------
# Backend liveness probe (per classificare gli skip runtime)
# ------------------------------------------------------------
BACKEND_PROBE_URL = os.environ.get(
    'PRE_QA_SAFETY_BACKEND_PROBE_URL', 'http://127.0.0.1:8001/api/health'
)
BACKEND_PROBE_TIMEOUT_S = 2.0


def _backend_is_up() -> bool:
    try:
        req = urllib.request.Request(BACKEND_PROBE_URL, method='GET')
        with urllib.request.urlopen(req, timeout=BACKEND_PROBE_TIMEOUT_S) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        return False


# ------------------------------------------------------------
# Suite definition
# ------------------------------------------------------------
# kind:
#   - 'validator'      : statico, deve sempre poter girare.
#   - 'smoke_static'   : smoke che NON richiede backend (statico).
#   - 'smoke_runtime'  : smoke che richiede backend up; se backend down →
#                        SKIPPED_BACKEND_DOWN (no falso PASS).
#   - 'rollup'         : aggregatore che esegue figli.
SUITE = [
    # Pack 113 — HomeOverflow nav guard
    {
        'name': 'Validator 113 HomeOverflow',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_113_home_overflow_guard.py',
    },
    {
        'name': 'Smoke 113 HomeOverflow',
        'kind': 'smoke_static',
        'script': 'smoke_pre_qa_stabilization_113_home_overflow_nav_guard.py',
    },
    # Pack 114 — Home routes canonicalization
    {
        'name': 'Validator 114 Home Routes',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_114_home_routes_canonicalization.py',
    },
    {
        'name': 'Smoke 114 Home Routes',
        'kind': 'smoke_static',
        'script': 'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py',
    },
    {
        'name': 'Rollup 114 Home Routes',
        'kind': 'rollup',
        'script': 'validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py',
    },
    # Pack 114B — Gacha/Combat lobby guard
    {
        'name': 'Validator 114B Gacha/Combat/Lobby Guard',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_114_gacha_combat_lobby_guard.py',
    },
    # Pack 115A — P0 hard gates / Home fix
    {
        'name': 'Validator 115A P0 Hard Gates',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115a_p0_hard_gates_home_fix.py',
    },
    {
        'name': 'Smoke 115A P0 Hard Gates',
        'kind': 'smoke_runtime',
        'script': 'smoke_pre_qa_stabilization_115a_p0_hard_gates_home_fix.py',
    },
    # Pack 115B — Progression/Forge/Items mutation gates
    {
        'name': 'Validator 115B Progression/Forge/Items',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115b_progression_forge_items_gates.py',
    },
    {
        'name': 'Smoke 115B Progression/Forge/Items',
        'kind': 'smoke_runtime',
        'script': 'smoke_pre_qa_stabilization_115b_progression_forge_items_gates.py',
    },
    # Pack 115C — Auth/server-scope unification
    {
        'name': 'Validator 115C Auth/Server Scope',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115c_auth_server_scope_unification.py',
    },
    # Pack 115D — Screen-entry / deeplink guard
    {
        'name': 'Validator 115D Screen-Entry/Deeplink Guard',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115d_screen_entry_deeplink_guard.py',
    },
    # Pack 115E — Combat/Tower legacy hardening
    {
        'name': 'Validator 115E Combat/Tower Legacy Hardening',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115e_combat_tower_legacy_hardening.py',
    },
    # Pack 115F — Repo hygiene + validator truth
    {
        'name': 'Validator 115F Repo Hygiene & Validator Truth',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py',
    },
    # Pack 115G — Skill/Artifact semantic cleanup
    {
        'name': 'Validator 115G Skill/Artifact Semantic Cleanup',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_115g_skill_artifact_semantic_cleanup.py',
    },
    # Pack 116A — Battle Power foundation (read-only, derived, server-scoped)
    {
        'name': 'Validator 116A Battle Power Foundation',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_116a_battle_power_foundation.py',
    },
    # Pack 116A-EXT — Hero card power + Bible source map
    {
        'name': 'Validator 116A-EXT Hero Card Power + Bible Source Map',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py',
    },
    # Pack 116A-EXT FIX-A — Team power source truth
    {
        'name': 'Validator 116A-EXT FIX-A Team Power Source Truth',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py',
    },
    # Pack 116B — Chat/Bot quality + legacy chat cleanup
    {
        'name': 'Validator 116B Chat/Bot Quality + Legacy Chat Cleanup',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py',
    },
    # Pack 116C — Red Dot notification badge foundation (read-only)
    {
        'name': 'Validator 116C Red Dot Notification Badge Foundation',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_116c_red_dot_notification_badge_foundation.py',
    },
    # Pack 117A — Manual QA gate + deferred resolver readiness (diagnostic)
    {
        'name': 'Validator 117A Manual QA Gate + Deferred Resolver Readiness',
        'kind': 'validator',
        'script': 'validate_pre_qa_stabilization_117a_manual_qa_gate_and_deferred_resolver_readiness.py',
    },
]

MAX_TAIL = 1500  # caratteri di stdout/stderr da preservare nel JSON.


def _tail(s: str, n: int = MAX_TAIL) -> str:
    if not s:
        return ''
    if len(s) <= n:
        return s
    return '...[truncated]...\n' + s[-n:]


def _run_one(entry: dict, backend_up: bool) -> dict:
    name = entry['name']
    kind = entry['kind']
    script_name = entry['script']
    script_fp = os.path.join(SCRIPTS, script_name)
    cmd = [sys.executable, script_fp]
    started = time.time()

    if not os.path.exists(script_fp):
        return {
            'name': name,
            'kind': kind,
            'script': script_name,
            'command': cmd,
            'returncode': None,
            'status': 'SKIPPED_REASON_EXPLICIT',
            'reason': f'script figlio mancante: {script_name}',
            'duration_s': 0.0,
            'stdout_tail': '',
            'stderr_tail': '',
        }

    # Skip esplicito per smoke runtime se backend e' down (mai falso PASS).
    if kind == 'smoke_runtime' and not backend_up:
        return {
            'name': name,
            'kind': kind,
            'script': script_name,
            'command': cmd,
            'returncode': None,
            'status': 'SKIPPED_BACKEND_DOWN',
            'reason': f'backend non raggiungibile su {BACKEND_PROBE_URL}',
            'duration_s': 0.0,
            'stdout_tail': '',
            'stderr_tail': '',
        }

    try:
        proc = subprocess.run(
            cmd,
            cwd=R,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        rc = proc.returncode
        status = 'PASS' if rc == 0 else 'FAIL'
        reason = '' if rc == 0 else f'returncode={rc}'
        return {
            'name': name,
            'kind': kind,
            'script': script_name,
            'command': cmd,
            'returncode': rc,
            'status': status,
            'reason': reason,
            'duration_s': round(time.time() - started, 3),
            'stdout_tail': _tail(proc.stdout),
            'stderr_tail': _tail(proc.stderr),
        }
    except subprocess.TimeoutExpired as e:
        return {
            'name': name,
            'kind': kind,
            'script': script_name,
            'command': cmd,
            'returncode': None,
            'status': 'FAIL',
            'reason': f'timeout dopo {e.timeout}s',
            'duration_s': round(time.time() - started, 3),
            'stdout_tail': _tail(e.stdout or ''),
            'stderr_tail': _tail(e.stderr or ''),
        }
    except Exception as e:  # pragma: no cover
        return {
            'name': name,
            'kind': kind,
            'script': script_name,
            'command': cmd,
            'returncode': None,
            'status': 'FAIL',
            'reason': f'eccezione runner: {type(e).__name__}: {e}',
            'duration_s': round(time.time() - started, 3),
            'stdout_tail': '',
            'stderr_tail': '',
        }


def main() -> int:
    backend_up = _backend_is_up()
    started_at = datetime.now(timezone.utc).isoformat()
    started_mono = time.time()

    results = []
    for entry in SUITE:
        res = _run_one(entry, backend_up)
        results.append(res)
        # Print stato live (un-line per item).
        marker = {
            'PASS': '✓',
            'FAIL': '✗',
            'SKIPPED_BACKEND_DOWN': '~',
            'SKIPPED_REASON_EXPLICIT': '~',
        }.get(res['status'], '?')
        print(f"  [{marker}] {res['status']:<24} {res['name']}"
              + (f"  ({res['reason']})" if res['reason'] else ''))

    finished_at = datetime.now(timezone.utc).isoformat()
    total_duration = round(time.time() - started_mono, 3)

    passed = [r for r in results if r['status'] == 'PASS']
    failed = [r for r in results if r['status'] == 'FAIL']
    skipped = [r for r in results if r['status'].startswith('SKIPPED_')]

    report = {
        'suite': 'PRE_QA_SAFETY_VALIDATOR_SUITE',
        'pack_origin': '115F',
        'started_at_utc': started_at,
        'finished_at_utc': finished_at,
        'total_duration_s': total_duration,
        'backend_probe_url': BACKEND_PROBE_URL,
        'backend_up': backend_up,
        'totals': {
            'total': len(results),
            'passed': len(passed),
            'failed': len(failed),
            'skipped': len(skipped),
        },
        'verdict': 'PRE_QA_SAFETY_SUITE_PASS' if not failed else 'PRE_QA_SAFETY_SUITE_FAIL',
        'results': results,
    }

    # Nome file con timestamp per audit storico.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_fp = os.path.join(REPORTS_DIR, f'pre_qa_safety_validator_suite_{stamp}.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Latest pointer per integrazione con altri tool.
    latest_fp = os.path.join(REPORTS_DIR, 'pre_qa_safety_validator_suite_latest.json')
    try:
        if os.path.exists(latest_fp):
            os.remove(latest_fp)
        shutil.copy2(out_fp, latest_fp)
    except OSError:
        pass

    print('')
    print('================ PRE-QA SAFETY SUITE — RIASSUNTO ================')
    print(f"  totali:  {report['totals']['total']}")
    print(f"  PASS:    {report['totals']['passed']}")
    print(f"  FAIL:    {report['totals']['failed']}")
    print(f"  SKIPPED: {report['totals']['skipped']}")
    print(f"  backend_up: {backend_up}")
    print(f"  verdict: {report['verdict']}")
    print(f"  JSON:    {out_fp}")
    print(f"  latest:  {latest_fp}")
    print('=================================================================')

    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
