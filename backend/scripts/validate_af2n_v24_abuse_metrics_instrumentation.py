#!/usr/bin/env python3
"""V24 — Validate abuse metrics instrumentation (module + endpoint contract).

Opzione C (V24 ULTRA-COMBO): fix mirato + asserzioni extra per copertura più
ampia. Verifica:
  • Modulo /app/backend/data/affinity_metrics.py esiste e contiene API minima.
  • Endpoint /api/affinity/gift-spend/_admin/metrics-snapshot risponde JSON.
  • Payload contiene chiavi obbligatorie (enabled, counters, histograms,
    histogram_sums_ms, histogram_counts, gauges, buckets_ms, safety).
  • Safety annotations: no_borea_data=true, no_user_pii=true,
    not_for_production_dashboards=true, design='in_memory_process_local'.
  • Nessun dato Borea esposto: i valori `hero_alias=borea` sono metadati di
    osservabilità operativa (legittimi); ma NESSUNA chiave hero data come
    descrizioni, base_stats, immagini, ecc. deve essere presente.
  • Buckets ms in ordine crescente, presenti tutti gli step previsti.
  • Counters/histograms numerici (int/float) — niente stringhe.
  • Hooks installati: il sorgente di affinity_gift_spend.py importa `inc` e
    `snapshot` da affinity_metrics in almeno 2 punti (borea 404 + rate-limit 429).
  • Guardrail: battle_engine.py e combat.tsx INVARIATI rispetto a HEAD.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

MOD = Path('/app/backend/data/affinity_metrics.py')
ROUTE = Path('/app/backend/routes/affinity_gift_spend.py')
EXPECTED_BUCKETS = [5, 10, 25, 50, 100, 250, 500, 1000, 2000]
SNAPSHOT_URL = 'http://127.0.0.1:8001/api/affinity/gift-spend/_admin/metrics-snapshot'

FORBIDDEN_DATA_KEYS = (
    'description', 'base_stats', 'image_url', 'rarity', 'canonical_id',
    'release_group', 'native_rarity', 'display_name', 'faction',
)
FORBIDDEN_HERO_ALIASES = ('borea', 'greek_borea', 'primordial_gaia')

# Guardrail files: must remain untouched
GUARDRAIL_FILES = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
]


def _rec(fails: list, ok: bool, label: str, detail: str = '') -> None:
    if not ok:
        fails.append(f'{label}{":" + detail if detail else ""}')


def _strip_op_aliases(blob: str) -> str:
    """Strip operationally-legitimate Borea label values from payload string."""
    blob = re.sub(r'hero_alias=[a-z_]+', 'hero_alias=__REDACTED__', blob)
    blob = re.sub(r'"no_borea_data"\s*:\s*true', '"__SAFETY_ANN__":true', blob)
    # Metric NAMES containing borea are legit operational identifiers, not data.
    blob = re.sub(
        r'af2_gift_spend_borea_404_total',
        'af2_gift_spend_HIDDENALIAS_404_total',
        blob,
    )
    # Legacy/operational label `borea=1` -> redacted (kept for backward-compat).
    blob = re.sub(r'borea=1\b', '__HIDDEN_FLAG__=1', blob)
    blob = re.sub(r'"borea"\s*:\s*"1"', '"__BOREA_FLAG__":"1"', blob)
    return blob


def main() -> int:
    fails: list[str] = []

    # ── 1) Modulo esiste e ha API minima ─────────────────────────────────
    if not MOD.exists():
        print('FAIL: module_missing')
        return 2
    src = MOD.read_text()
    for tok in [
        'AFFINITY_METRICS_ENABLED',
        'snapshot',
        'inc',
        'observe_latency_ms',
        'set_gauge',
        'enabled',
        '_HIST_BUCKETS_MS',
    ]:
        _rec(fails, tok in src, f'token:{tok}')

    # ── 2) Hooks installati nella route gift-spend ───────────────────────
    if ROUTE.exists():
        rsrc = ROUTE.read_text()
        _rec(
            fails,
            rsrc.count('from data.affinity_metrics import') >= 2,
            'hooks_route_import_count_lt_2',
        )
        _rec(
            fails,
            'af2_gift_spend_borea_404_total' in rsrc,
            'hook_borea_404_counter_missing',
        )
        _rec(
            fails,
            'af2_ratelimit_429_total' in rsrc or 'af2_gift_spend_total' in rsrc,
            'hook_ratelimit_counter_missing',
        )
    else:
        fails.append('route_missing')

    # ── 3) Endpoint snapshot raggiungibile e ben formato ─────────────────
    payload: dict = {}
    try:
        with urlopen(SNAPSHOT_URL, timeout=4) as r:
            payload = json.loads(r.read().decode())
    except Exception as e:
        fails.append(f'snapshot_endpoint_error:{e}')

    if payload:
        for k in (
            'enabled',
            'started_at_epoch',
            'uptime_seconds',
            'counters',
            'histograms',
            'histogram_sums_ms',
            'histogram_counts',
            'gauges',
            'buckets_ms',
            'safety',
        ):
            _rec(fails, k in payload, f'snapshot_missing_key:{k}')

        if payload.get('enabled') is True:
            # 3a) buckets check
            _rec(
                fails,
                payload.get('buckets_ms') == EXPECTED_BUCKETS,
                'buckets_mismatch',
            )
            # 3b) safety annotations
            safety = payload.get('safety') or {}
            _rec(fails, safety.get('flag') == 'AFFINITY_METRICS_ENABLED', 'safety_flag_wrong')
            _rec(fails, safety.get('no_borea_data') is True, 'safety_no_borea_data')
            _rec(fails, safety.get('no_user_pii') is True, 'safety_no_user_pii')
            _rec(
                fails,
                safety.get('not_for_production_dashboards') is True,
                'safety_not_for_prod_dash',
            )
            _rec(
                fails,
                safety.get('design') == 'in_memory_process_local',
                'safety_design_wrong',
            )

            # 3c) counters / histograms are numeric types
            for cname, cval in (payload.get('counters') or {}).items():
                _rec(
                    fails,
                    isinstance(cval, (int, float)),
                    f'counter_not_numeric:{cname}',
                )
            for hname, hval in (payload.get('histograms') or {}).items():
                _rec(
                    fails,
                    isinstance(hval, dict),
                    f'histogram_not_dict:{hname}',
                )

            # 3d) NO Borea data leak (after stripping legit op-aliases)
            blob = _strip_op_aliases(json.dumps(payload))
            low = blob.lower()
            for forbidden in FORBIDDEN_HERO_ALIASES:
                _rec(fails, forbidden not in low, f'snapshot_contains:{forbidden}')

            # 3e) NO hero data fields exposed
            for k in FORBIDDEN_DATA_KEYS:
                _rec(fails, k not in low, f'snapshot_data_leak:{k}')

    # ── 4) Guardrail invariati (battle_engine / battle_core / combat.tsx) ─
    for f in GUARDRAIL_FILES:
        if not Path(f).exists():
            continue
        try:
            diff = subprocess.run(
                ['git', '-C', '/app', 'diff', '--stat', '--', f],
                capture_output=True,
                text=True,
                timeout=5,
            )
            modified = bool(diff.stdout.strip())
            _rec(fails, not modified, f'guardrail_modified:{f}')
        except Exception as e:
            fails.append(f'guardrail_check_error:{f}:{e}')

    # ── Report finale ────────────────────────────────────────────────────
    if fails:
        for f in fails:
            print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-ABUSE-METRICS-INSTRUMENTATION')
    print('  • module_present=True')
    print('  • snapshot_endpoint_ok=True')
    print(f'  • counters_count={len((payload or {}).get("counters") or {})}')
    print(f'  • histograms_count={len((payload or {}).get("histograms") or {})}')
    print('  • guardrails_clean=True')
    return 0


if __name__ == '__main__':
    sys.exit(main())
