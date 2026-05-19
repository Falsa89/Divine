#!/usr/bin/env python3
"""V24 — Real Observation Window for Stage 4 Internal Beta.

Esercita il sistema con traffico realistico, anonimo, e cattura metriche
reali via /api/affinity/gift-spend/_admin/metrics-snapshot e /canary-status.

Operazioni (tutte SAFE):
  1. /api/health probe
  2. /api/heroes count == 100 invariant
  3. 3× Borea-alias probes (devono → 404)
  4. N× canary gift-spend (idempotency unique, allowlist users)
  5. 1× burst per indurre 429 e popolare ratelimit counters
  6. Snapshot finale + canary-status finale

Output: /app/backend/reports/v24_real_observation_window.json
"""
from __future__ import annotations
import json, os, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = 'http://127.0.0.1:8001'
REPORT_DIR = Path('/app/backend/reports')
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUT = REPORT_DIR / 'v24_real_observation_window.json'


def _get(path: str) -> tuple[int, dict | list | str]:
    req = Request(BASE + path)
    try:
        with urlopen(req, timeout=5) as r:
            txt = r.read().decode()
            try:
                return r.status, json.loads(txt)
            except Exception:
                return r.status, txt
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, str(e)
    except URLError as e:
        return -1, str(e)


def _post(path: str, payload: dict) -> tuple[int, dict | str]:
    body = json.dumps(payload).encode()
    req = Request(BASE + path, data=body, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as r:
            txt = r.read().decode()
            try:
                return r.status, json.loads(txt)
            except Exception:
                return r.status, txt
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, str(e)
    except URLError as e:
        return -1, str(e)


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    out: dict = {
        'task_origin': 'AF2-N-V24-REAL-OBSERVATION-WINDOW',
        'started_at_utc': started,
        'safety_invariants': [
            'borea_aliases_404',
            'api_heroes_count_100',
            'no_5xx',
            'battle_engine_untouched',
            'broad_rollout_off',
        ],
        'phases': {},
    }

    # ── Phase 1: health ────────────────────────────────────────────────
    code, h = _get('/api/health')
    out['phases']['health'] = {'http': code, 'ok': code == 200 and isinstance(h, dict) and h.get('status') == 'ok'}

    # ── Phase 2: heroes count ──────────────────────────────────────────
    code, heroes = _get('/api/heroes')
    cnt = len(heroes) if isinstance(heroes, list) else -1
    ids = {(x.get('id') or '').lower() for x in heroes} if isinstance(heroes, list) else set()
    leak = ids & {'borea', 'greek_borea', 'primordial_gaia'}
    out['phases']['heroes_count'] = {'http': code, 'count': cnt, 'expected': 100, 'ok': cnt == 100, 'borea_leak': sorted(leak)}

    # ── Phase 3: Borea alias probes (must → 404) ───────────────────────
    borea_probes = []
    for alias in ('borea', 'greek_borea', 'primordial_gaia'):
        c, _ = _post('/api/affinity/gift-spend', {
            'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
            'idempotency_key': f'v24_obs_{alias}_{uuid.uuid4().hex[:6]}',
            'user_id': 'stage4_qa_001',
        })
        borea_probes.append({'alias': alias, 'http': c, 'ok': c == 404})
    out['phases']['borea_probes'] = borea_probes
    out['phases']['borea_all_404'] = all(p['ok'] for p in borea_probes)

    # ── Phase 4: canary gift-spend (real allowlist users) ──────────────
    spend_results = []
    spend_users = [f'stage4_qa_{i:03d}' for i in range(1, 11)]  # 10 spends, 1 each
    for uid in spend_users:
        c, body = _post('/api/affinity/gift-spend', {
            'gift_id': 'gift_test_001',
            'hero_id': 'greek_ares',
            'quantity': 1,
            'idempotency_key': f'v24_obs_spend_{uid}_{uuid.uuid4().hex[:8]}',
            'user_id': uid,
        })
        spend_results.append({'user': uid, 'http': c, 'ok': c in (200, 201)})
        # tiny pace to not trigger burst limit
        time.sleep(0.02)
    out['phases']['canary_spends'] = {
        'attempted': len(spend_results),
        'succeeded': sum(1 for r in spend_results if r['ok']),
        'details': spend_results,
    }

    # ── Phase 5: induced burst (must produce at least one 429) ────────
    burst_user = 'stage4_qa_500'
    burst_results = []
    for i in range(10):
        c, _ = _post('/api/affinity/gift-spend', {
            'gift_id': 'gift_test_001',
            'hero_id': 'greek_ares',
            'quantity': 1,
            'idempotency_key': f'v24_obs_burst_{i}_{uuid.uuid4().hex[:6]}',
            'user_id': burst_user,
        })
        burst_results.append(c)
    out['phases']['induced_burst'] = {
        'user': burst_user,
        'sequence': burst_results,
        'at_least_one_429': 429 in burst_results,
        'no_5xx': all(c < 500 for c in burst_results),
    }

    # ── Phase 6: snapshots ─────────────────────────────────────────────
    _, snap = _get('/api/affinity/gift-spend/_admin/metrics-snapshot')
    _, canary = _get('/api/affinity/gift-spend/canary-status')
    out['phases']['metrics_snapshot'] = snap if isinstance(snap, dict) else {'error': str(snap)}
    out['phases']['canary_status'] = canary if isinstance(canary, dict) else {'error': str(canary)}

    # ── Final verdict ──────────────────────────────────────────────────
    pass_conditions = [
        out['phases']['health']['ok'],
        out['phases']['heroes_count']['ok'],
        not out['phases']['heroes_count']['borea_leak'],
        out['phases']['borea_all_404'],
        out['phases']['canary_spends']['succeeded'] >= 5,
        out['phases']['induced_burst']['no_5xx'],
    ]
    out['verdict'] = 'PASS' if all(pass_conditions) else 'FAIL'
    out['ended_at_utc'] = datetime.now(timezone.utc).isoformat()

    OUT.write_text(json.dumps(out, indent=2, default=str))

    # Print summary
    print(f"VERDICT: {out['verdict']}")
    print(f"  health.ok = {out['phases']['health']['ok']}")
    print(f"  heroes_count = {out['phases']['heroes_count']['count']} / 100")
    print(f"  borea_all_404 = {out['phases']['borea_all_404']}")
    print(f"  canary_spends = {out['phases']['canary_spends']['succeeded']} / {out['phases']['canary_spends']['attempted']}")
    print(f"  induced_burst.at_least_one_429 = {out['phases']['induced_burst']['at_least_one_429']}")
    print(f"  induced_burst.no_5xx = {out['phases']['induced_burst']['no_5xx']}")
    print(f"  rate_limit_backend = {out['phases']['canary_status'].get('rate_limit_backend')}")
    print(f"  ledger_canary_rows = {out['phases']['canary_status'].get('ledger_canary_rows')}")
    snap_counters = (out['phases']['metrics_snapshot'].get('counters') or {}) if isinstance(out['phases']['metrics_snapshot'], dict) else {}
    print(f"  metrics_counters_unique_keys = {len(snap_counters)}")
    if snap_counters:
        print('  counters (top 10):')
        for k, v in list(snap_counters.items())[:10]:
            print(f'    {k} = {v}')
    print(f"\nReport written: {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
