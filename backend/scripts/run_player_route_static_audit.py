#!/usr/bin/env python3
"""PROJECT_BETA_TESTING_AUTOMATION_HARNESS Track B — Player Route Static Audit.

Deterministic, READ-ONLY static analysis of player-facing routes.
Writes a JSON report to /app/backend/reports/player_route_static_audit_latest.json

Rules per route:
  - Must export default a component.
  - For locked surfaces (shop, item-shop, gacha, battlepass, vip, artifacts-preview,
    economy, exclusive, servers): must NOT contain live mutation API calls,
    or must declare an explicit lock flag (e.g. SHOP_LOCKED_V2 = true).
  - Bypass guards: no apiCall to forbidden mutation endpoints.
  - Modal anti-pattern: no <Modal> + <KeyboardAvoidingView> + nested ScrollView + TextInput
    combination (the pattern that crashed Soul Forge on mobile).

Usage:
    python3 /app/backend/scripts/run_player_route_static_audit.py

Exits 0 on success (with PASS/WARN summary). Failures append entries to the JSON
but do not exit non-zero (the dedicated validator does the strict gate).
"""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRONTEND_APP = Path('/app/frontend/app')
OUTPUT = Path('/app/backend/reports/player_route_static_audit_latest.json')

# Routes considered player-facing for this audit. Tuples of (display_name, relative_path).
PLAYER_ROUTES: list[tuple[str, str]] = [
    ('soul-forge.tsx', 'soul-forge.tsx'),
    ('treasury.tsx', 'treasury.tsx'),
    ('economy.tsx', 'economy.tsx'),
    ('exclusive.tsx', 'exclusive.tsx'),
    ('gacha.tsx', '(tabs)/gacha.tsx'),
    ('shop.tsx', 'shop.tsx'),
    ('item-shop.tsx', 'item-shop.tsx'),
    ('battlepass.tsx', 'battlepass.tsx'),
    ('vip.tsx', 'vip.tsx'),
    ('servers.tsx', 'servers.tsx'),
    ('safe-previews.tsx', 'safe-previews.tsx'),
    ('daily-hub.tsx', 'daily-hub.tsx'),
    ('artifacts-preview.tsx', 'artifacts-preview.tsx'),
]

# Routes that MUST be locked / read-only / preview-only on production builds.
LOCKED_ROUTES = {
    'shop.tsx':       {'flag': r'SHOP_LOCKED_V2\s*=\s*true'},
    'item-shop.tsx':  {'flag': r'ITEM_SHOP_LOCKED_V2\s*=\s*true'},
    'gacha.tsx':      {'flag': r'LOCKED_BANNERS_V2|GACHA_LOCKED_V2\s*=\s*true|_LOCKED_V2\s*=\s*true|IN REVISIONE'},
    'battlepass.tsx': {'flag': r'BATTLEPASS_LOCKED_V2\s*=\s*true|_LOCKED_V2\s*=\s*true'},
    'vip.tsx':        {'flag': r'VIP_LOCKED_V2\s*=\s*true|_LOCKED_V2\s*=\s*true'},
    'exclusive.tsx':  {'flag': r'Schermata legacy archiviata'},
    'economy.tsx':    {'flag': r"router\.replace\('/soul-forge'\)"},
    'servers.tsx':    {'flag': r'_LOCKED_V2\s*=\s*true|legacy|preview'},
}

# API calls considered live-mutation. If they appear in a locked file without
# being commented out or inside a code path guarded by the lock flag, FAIL.
FORBIDDEN_LIVE_MUTATIONS = [
    r"apiCall\('/api/shops/buy'",
    r"apiCall\('/api/shop/buy'",
    r"apiCall\('/api/item-shop/buy'",
    r"apiCall\('/api/gacha/pull'",
    r"apiCall\('/api/battlepass/claim'",
    r"apiCall\('/api/battlepass/purchase'",
    r"apiCall\('/api/vip/purchase'",
    r"apiCall\('/api/exclusive/craft'",
    r"apiCall\('/api/soul-forge/retire'",
    r"apiCall\('/api/equipment/forge'",
]

# Soul Forge MUST keep the inline confirm panel (no <Modal> in the confirm path).
SOUL_FORGE_REQUIRED_MARKERS = [
    r'inlineConfirmOpen',
    r'inlineConfirmCard',
    r"apiCall\('/api/soul/forge'",
]
SOUL_FORGE_FORBIDDEN_MARKERS = [
    r'<Modal\b',
    r'<KeyboardAvoidingView\b',
    r'\bsetConfirmOpen\b',
    r"\bfrom 'react-native';[\s\S]{0,200}\bModal\b",  # Modal in react-native import
]


def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def strip_comments(t: str) -> str:
    """Remove // and /* */ comments to avoid false positives on documentation."""
    t = re.sub(r'/\*[\s\S]*?\*/', '', t)
    t = re.sub(r'(^|[^:\"\'])//[^\n]*', r'\1', t)
    return t


def audit_route(display: str, rel: str) -> dict[str, Any]:
    p = FRONTEND_APP / rel
    out: dict[str, Any] = {
        'route': display,
        'path': rel,
        'exists': p.exists(),
        'md5': None,
        'has_default_export': None,
        'has_lock_flag': None,
        'lock_flag_gates_mutations': None,
        'forbidden_mutations_found': [],
        'soul_forge_inline_confirm_markers_ok': None,
        'soul_forge_modal_path_absent': None,
        'verdict': 'PASS',
        'notes': [],
    }
    if not p.exists():
        out['verdict'] = 'MISS'
        out['notes'].append('file missing')
        return out
    raw = p.read_text(encoding='utf-8', errors='replace')
    out['md5'] = md5_of(p)
    out['has_default_export'] = bool(re.search(r'export\s+default\s+', raw))
    if not out['has_default_export']:
        out['verdict'] = 'WARN'
        out['notes'].append('no default export')

    # Strip comments for content scans.
    code = strip_comments(raw)

    # Locked-route checks.
    lock_flag_name = None
    if display in LOCKED_ROUTES:
        flag_pat = LOCKED_ROUTES[display]['flag']
        m = re.search(flag_pat, code)
        out['has_lock_flag'] = bool(m)
        if m:
            # Extract the flag identifier (best effort) for the gate check.
            m2 = re.search(r'([A-Z_][A-Z0-9_]+_LOCKED_V2)', code)
            if m2:
                lock_flag_name = m2.group(1)
        if not out['has_lock_flag']:
            out['verdict'] = 'WARN'
            out['notes'].append(f'missing lock marker matching {flag_pat!r}')

    # Forbidden live mutations: collect raw hits, then determine if they are
    # SAFELY gated by an `if (LOCKED_FLAG) return;` early-return preceding them.
    for pat in FORBIDDEN_LIVE_MUTATIONS:
        if re.search(pat, code):
            out['forbidden_mutations_found'].append(pat)

    if out['forbidden_mutations_found']:
        # Default: FAIL unless we can prove all mutation call sites are gated.
        gate_ok = False
        if lock_flag_name:
            # Heuristic: look for `if (<FLAG>) return` in the same function scope.
            # We accept it if at least one such gate exists in the file (the file is
            # short and lock-aware by design).
            gate_pat = rf'if\s*\(\s*{re.escape(lock_flag_name)}\s*\)\s*return'
            gate_ok = bool(re.search(gate_pat, code))
        out['lock_flag_gates_mutations'] = gate_ok
        if gate_ok:
            out['verdict'] = 'PASS'
            out['notes'].append(
                f'mutation calls present but gated by `if ({lock_flag_name}) return` early-return'
            )
        else:
            out['verdict'] = 'FAIL'
            out['notes'].append('live mutation api call NOT gated by lock flag')

    # Soul-forge specific: confirm path must be inline, not Modal.
    if display == 'soul-forge.tsx':
        missing = [pp for pp in SOUL_FORGE_REQUIRED_MARKERS if not re.search(pp, code)]
        out['soul_forge_inline_confirm_markers_ok'] = not missing
        if missing:
            out['verdict'] = 'FAIL'
            out['notes'].append(f'soul forge missing inline markers: {missing}')
        forbidden_hits = [pp for pp in SOUL_FORGE_FORBIDDEN_MARKERS if re.search(pp, code)]
        out['soul_forge_modal_path_absent'] = not forbidden_hits
        if forbidden_hits:
            out['verdict'] = 'FAIL'
            out['notes'].append(f'soul forge contains Modal-path markers: {forbidden_hits}')

    return out


def main() -> int:
    results = [audit_route(display, rel) for display, rel in PLAYER_ROUTES]
    summary = {
        'task': 'PROJECT_BETA_TESTING_AUTOMATION_HARNESS_AND_REDIS_STABILIZATION',
        'track': 'B',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'routes_audited': len(results),
        'pass': sum(1 for r in results if r['verdict'] == 'PASS'),
        'warn': sum(1 for r in results if r['verdict'] == 'WARN'),
        'fail': sum(1 for r in results if r['verdict'] == 'FAIL'),
        'miss': sum(1 for r in results if r['verdict'] == 'MISS'),
        'results': results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(summary, indent=2))
    print(f'[player_route_static_audit] pass={summary["pass"]} warn={summary["warn"]} fail={summary["fail"]} miss={summary["miss"]}')
    for r in results:
        if r['verdict'] != 'PASS':
            print(f"  {r['verdict']} {r['route']}: {r['notes']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
