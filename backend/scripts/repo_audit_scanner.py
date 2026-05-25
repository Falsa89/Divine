#!/usr/bin/env python3
"""
PROJECT_FULL_REPO_CONSISTENCY_AUDIT_AND_MASTER_FIX_PLAN_PACK
Scanner deterministico unico.

Output: 6 JSON canonici (sorted, no timestamps variabili) sotto
/app/data/design/audit/full_repo/
  - frontend_route_menu_registry_v1.json        (Track A)
  - frontend_api_callsite_registry_v1.json      (Track B)
  - backend_endpoint_mutation_registry_v1.json  (Track C)
  - feature_mode_crosswalk_v1.json              (Track D)
  - economy_gacha_roster_risk_audit_v1.json     (Track E)
  - gates_locked_preview_dev_surface_audit_v1.json (Track F)

Vincoli: read-only. Nessuna mutazione DB / runtime.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path('/app')
OUT_DIR = Path('/app/data/design/audit/full_repo')
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRONTEND_APP = ROOT / 'frontend' / 'app'
FRONTEND_COMPONENTS = ROOT / 'frontend' / 'components'
FRONTEND_CONTEXT = ROOT / 'frontend' / 'context'
FRONTEND_UTILS = ROOT / 'frontend' / 'utils'
FRONTEND_CONSTANTS = ROOT / 'frontend' / 'constants'
BACKEND = ROOT / 'backend'
BACKEND_ROUTES = BACKEND / 'routes'

SCAN_ROOTS = [
    FRONTEND_APP, FRONTEND_COMPONENTS, FRONTEND_CONTEXT,
    FRONTEND_UTILS, FRONTEND_CONSTANTS,
    BACKEND,
    ROOT / 'data' / 'design',
    ROOT / 'docs' / 'divine',
]


# ----------------------------- helpers -----------------------------

def _read(p: Path) -> str | None:
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None


def _rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def _walk(root: Path, exts: tuple[str, ...]) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix not in exts:
            continue
        # skip node_modules, __pycache__, .git
        rel = _rel(p)
        if any(seg in rel for seg in ('node_modules', '__pycache__', '.git/', '/.expo/')):
            continue
        out.append(p)
    return sorted(out, key=lambda x: _rel(x))


# Tag classifications ------------------------------------------------
SAFE_PREVIEW_HINTS = (
    'safe-previews', 'artifacts-preview', 'housing-preview', 'status-codex',
    'collection-synergies-preview', 'affinity-gifts-preview',
    'divine-weapons-catalog', 'hero-skill-kits-catalog', 'hero-encyclopedia',
)
DEV_HINTS = (
    'sprite-test', 'dev-combat-qa-lab', 'qa-lab', '/dev-', '/debug-',
)
LOCKED_LIVE_LOCK_HINTS = (
    'locked', 'preview only', 'sola lettura', 'inert', '503',
)


def _classify_route(rel_path: str, text: str) -> str:
    low = rel_path.lower()
    if any(h in low for h in SAFE_PREVIEW_HINTS):
        return 'LOCKED_PREVIEW'
    if any(h in low for h in DEV_HINTS):
        return 'DEV_ONLY'
    # Check text-based locked indicator
    if text and any(h in text.lower() for h in LOCKED_LIVE_LOCK_HINTS):
        if 'apiCall' not in text and 'fetch(' not in text:
            return 'LOCKED_PREVIEW'
    return 'UNCLASSIFIED'


# ----------------------------- TRACK A -----------------------------

def build_frontend_route_menu_registry() -> dict:
    """Scansiona /app/frontend/app per route Expo + menu entries."""
    routes: list[dict] = []
    tsx_files = _walk(FRONTEND_APP, ('.tsx', '.ts'))
    for p in tsx_files:
        rel = _rel(p)
        text = _read(p) or ''
        # filename → route
        rel_to_app = p.relative_to(FRONTEND_APP)
        parts = list(rel_to_app.with_suffix('').parts)
        # skip _layout and components-only
        is_layout = parts[-1].startswith('_layout')
        # collapse group dirs like (tabs)
        route_parts = [s for s in parts if not (s.startswith('(') and s.endswith(')'))]
        route_str = '/' + '/'.join(route_parts)
        if route_str.endswith('/index'):
            route_str = route_str[: -len('/index')] or '/'
        flags: set[str] = set()
        low_text = text.lower()
        low_rel = rel.lower()
        if any(h in low_rel for h in SAFE_PREVIEW_HINTS):
            flags.add('LOCKED_PREVIEW')
        if any(h in low_rel for h in DEV_HINTS):
            flags.add('DEV_ONLY')
        if 'apicall(' in low_text or 'fetch(' in low_text:
            flags.add('HAS_API_CALLS')
        if re.search(r"method:\s*'(post|put|patch|delete)'", text, re.IGNORECASE):
            flags.add('LEGACY_LIVE_MUTATION')
        if 'router.push' in text or 'router.replace' in text:
            flags.add('NAVIGATES')
        if not flags:
            flags.add('UNCLASSIFIED')
        # final tag
        if 'LOCKED_PREVIEW' in flags:
            tag = 'LOCKED_PREVIEW'
        elif 'DEV_ONLY' in flags:
            tag = 'DEV_ONLY'
        elif 'LEGACY_LIVE_MUTATION' in flags:
            tag = 'LEGACY_LIVE'
        elif 'HAS_API_CALLS' in flags:
            tag = 'PLAYER_SAFE'
        else:
            tag = 'PLAYER_SAFE'
        routes.append({
            'file': rel,
            'route': route_str,
            'is_layout': is_layout,
            'tag': tag,
            'flags': sorted(flags),
        })

    # menu entries (from (tabs)/menu.tsx + daily-hub + safe-previews)
    menu_files = [
        FRONTEND_APP / '(tabs)' / 'menu.tsx',
        FRONTEND_APP / '(tabs)' / '_layout.tsx',
        FRONTEND_APP / 'daily-hub.tsx',
        FRONTEND_APP / 'safe-previews.tsx',
    ]
    menu_entries: list[dict] = []
    route_pattern = re.compile(r"route:\s*'([^']+)'")
    label_pattern = re.compile(r"label:\s*'([^']+)'")
    name_pattern = re.compile(r'name="([^"]+)"')
    for mf in menu_files:
        text = _read(mf) or ''
        if not text:
            continue
        # block-by-block heuristic: find label/route pairs on adjacent lines
        for m in re.finditer(r"\{\s*label:\s*'([^']+)'[^\}]*?route:\s*'([^']+)'", text, re.DOTALL):
            menu_entries.append({
                'source': _rel(mf),
                'label': m.group(1),
                'route': m.group(2),
            })
        # also Tabs.Screen name=
        for m in name_pattern.finditer(text):
            menu_entries.append({
                'source': _rel(mf),
                'label': m.group(1),
                'route': '/' + m.group(1),
                'kind': 'tab',
            })
    # dedupe + sort
    seen = set()
    deduped: list[dict] = []
    for e in menu_entries:
        key = (e.get('source'), e.get('label'), e.get('route'))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)
    deduped.sort(key=lambda e: (e.get('source', ''), e.get('label', '')))

    counts_by_tag: dict[str, int] = defaultdict(int)
    for r in routes:
        counts_by_tag[r['tag']] += 1

    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'A',
        'verdict': 'TRACK_A_FULL_FRONTEND_ROUTE_AND_MENU_REGISTRY_READY',
        'scan_root': _rel(FRONTEND_APP),
        'route_count': len(routes),
        'menu_entry_count': len(deduped),
        'counts_by_tag': dict(sorted(counts_by_tag.items())),
        'routes': sorted(routes, key=lambda r: r['file']),
        'menu_entries': deduped,
    }


# ----------------------------- TRACK B -----------------------------

API_CALL_PATTERNS = [
    # apiCall('/api/...', { method: 'POST' })
    re.compile(r"apiCall\(\s*[`'\"]([^`'\"]+)[`'\"]\s*(?:,\s*\{[^}]*method:\s*['\"]([A-Z]+)['\"][^}]*\})?", re.DOTALL),
    # fetch('/api/...', {...})
    re.compile(r"fetch\(\s*[`'\"]([^`'\"]+)[`'\"]\s*(?:,\s*\{[^}]*method:\s*['\"]([A-Z]+)['\"][^}]*\})?", re.DOTALL),
]
MUTATING_VERBS = {'POST', 'PUT', 'PATCH', 'DELETE'}
ECONOMY_HINTS = ('buy', 'claim', 'pull', 'equip', 'craft', 'fuse', 'retire',
                 'select', 'upgrade', 'use', 'spend', 'redeem', 'gift')


def build_frontend_api_callsite_registry() -> dict:
    callsites: list[dict] = []
    scan_roots = [FRONTEND_APP, FRONTEND_COMPONENTS, FRONTEND_CONTEXT,
                  FRONTEND_UTILS]
    files: list[Path] = []
    for r in scan_roots:
        files.extend(_walk(r, ('.tsx', '.ts')))
    for p in files:
        text = _read(p) or ''
        rel = _rel(p)
        for pat in API_CALL_PATTERNS:
            for m in pat.finditer(text):
                endpoint = m.group(1)
                method = (m.group(2) or 'GET').upper()
                if not endpoint.startswith(('/api/', 'http')):
                    # filter only api-like
                    continue
                low_ep = endpoint.lower()
                low_text_around = text[max(0, m.start() - 200): m.end() + 200].lower()
                mutating = method in MUTATING_VERBS
                hits_econ = any(h in low_ep for h in ECONOMY_HINTS)
                risk = 'low'
                if mutating and hits_econ:
                    risk = 'high'
                elif mutating:
                    risk = 'medium'
                # feature inference
                feature = 'unknown'
                for f in ('gacha', 'artifact', 'constellation', 'shop',
                          'battlepass', 'battle_pass', 'vip', 'hero',
                          'equipment', 'housing', 'server', 'auth',
                          'achievement', 'event', 'mail', 'pvp', 'raid',
                          'guild', 'tower', 'story', 'inventory',
                          'forge', 'exclusive', 'affinity', 'soul'):
                    if f in low_ep:
                        feature = f
                        break
                callsites.append({
                    'file': rel,
                    'endpoint': endpoint,
                    'method': method,
                    'mutating': mutating,
                    'feature': feature,
                    'risk': risk,
                })
    # dedupe by (file, endpoint, method)
    seen = set()
    deduped: list[dict] = []
    for c in callsites:
        key = (c['file'], c['endpoint'], c['method'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    deduped.sort(key=lambda c: (c['file'], c['endpoint'], c['method']))

    # by-feature counts
    by_feature_mut: dict[str, int] = defaultdict(int)
    for c in deduped:
        if c['mutating']:
            by_feature_mut[c['feature']] += 1

    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'B',
        'verdict': 'TRACK_B_FULL_FRONTEND_API_CALLSITE_AND_MUTATION_REGISTRY_READY',
        'callsite_count': len(deduped),
        'mutating_callsite_count': sum(1 for c in deduped if c['mutating']),
        'high_risk_count': sum(1 for c in deduped if c['risk'] == 'high'),
        'mutating_by_feature': dict(sorted(by_feature_mut.items())),
        'callsites': deduped,
    }


# ----------------------------- TRACK C -----------------------------

# FastAPI / Flask-like decorators
ENDPOINT_DECORATORS = [
    # @app.get("/path") | @router.post('/path')
    re.compile(r"@\w+\.(get|post|put|patch|delete)\(\s*[`'\"]([^`'\"]+)[`'\"]", re.IGNORECASE),
    # @api_router.get("/path")
    re.compile(r"@api_router\.(get|post|put|patch|delete)\(\s*[`'\"]([^`'\"]+)[`'\"]", re.IGNORECASE),
]
DB_WRITE_TOKENS = (
    'insert_one(', 'insert_many(', 'update_one(', 'update_many(',
    'replace_one(', 'delete_one(', 'delete_many(', 'find_one_and_update(',
    'find_one_and_replace(', 'find_one_and_delete(', 'bulk_write(',
)
DB_READ_TOKENS = ('find_one(', 'find(', 'count_documents(', 'aggregate(')


def _extract_endpoint_body(text: str, start_idx: int) -> str:
    """Extract a window after the decorator until next decorator/EOF."""
    next_dec = re.search(r'\n@\w+\.', text[start_idx + 1:])
    end = start_idx + 1 + next_dec.start() if next_dec else min(len(text), start_idx + 4000)
    return text[start_idx:end]


def build_backend_endpoint_registry() -> dict:
    endpoints: list[dict] = []
    py_files: list[Path] = []
    for r in (BACKEND, BACKEND_ROUTES):
        if r.exists():
            py_files.extend(_walk(r, ('.py',)))
    # dedupe by path
    py_files = sorted({p for p in py_files}, key=lambda x: _rel(x))
    api_prefix_re = re.compile(r"APIRouter\(\s*prefix\s*=\s*[`'\"]([^`'\"]+)[`'\"]")
    include_router_re = re.compile(r"include_router\(\s*\w+\s*,\s*prefix\s*=\s*[`'\"]([^`'\"]+)[`'\"]")
    for p in py_files:
        text = _read(p) or ''
        if not text:
            continue
        rel = _rel(p)
        # detect router prefix in this file
        prefixes = api_prefix_re.findall(text)
        prefix = prefixes[0] if prefixes else ''
        # detect prefixes from include_router elsewhere (best effort: skip)
        for pat in ENDPOINT_DECORATORS:
            for m in pat.finditer(text):
                method = m.group(1).upper()
                path_part = m.group(2)
                body = _extract_endpoint_body(text, m.start())
                db_writes = any(tok in body for tok in DB_WRITE_TOKENS)
                db_reads = any(tok in body for tok in DB_READ_TOKENS)
                auth_required = (
                    'get_current_user' in body or 'Depends(' in body
                    or 'verify_token' in body
                )
                is_inert = (
                    'raise HTTPException(status_code=503' in body
                    or 'status_code=503' in body
                    or 'feature unavailable' in body.lower()
                )
                low_path = path_part.lower()
                feature = 'unknown'
                for f in ('gacha', 'artifact', 'constellation', 'shop',
                          'battlepass', 'battle_pass', 'vip', 'hero',
                          'equipment', 'housing', 'server-profile', 'server',
                          'auth', 'login', 'achievement', 'event', 'mail',
                          'pvp', 'raid', 'guild', 'tower', 'story', 'inventory',
                          'forge', 'exclusive', 'affinity', 'soul', 'status',
                          'codex', 'admin', 'health', 'config', 'ledger',
                          'safety', 'canary'):
                    if f in low_path:
                        feature = f
                        break
                risk = 'low'
                if db_writes and method in MUTATING_VERBS:
                    risk = 'high'
                elif method in MUTATING_VERBS:
                    risk = 'medium'
                # full path with prefix
                full_path = (prefix + path_part).replace('//', '/')
                # treat /api/* normalization
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                endpoints.append({
                    'file': rel,
                    'path': full_path,
                    'method': method,
                    'mutating': method in MUTATING_VERBS,
                    'db_writes_in_body': db_writes,
                    'db_reads_in_body': db_reads,
                    'auth_required': auth_required,
                    'inert_503': is_inert,
                    'feature': feature,
                    'risk': 'inert' if is_inert else risk,
                })
    # dedupe
    seen = set()
    deduped: list[dict] = []
    for e in endpoints:
        key = (e['file'], e['path'], e['method'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)
    deduped.sort(key=lambda e: (e['file'], e['path'], e['method']))

    by_feature: dict[str, int] = defaultdict(int)
    by_feature_mut: dict[str, int] = defaultdict(int)
    for e in deduped:
        by_feature[e['feature']] += 1
        if e['mutating']:
            by_feature_mut[e['feature']] += 1
    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'C',
        'verdict': 'TRACK_C_FULL_BACKEND_ENDPOINT_AND_MUTATION_REGISTRY_READY',
        'endpoint_count': len(deduped),
        'mutating_endpoint_count': sum(1 for e in deduped if e['mutating']),
        'inert_503_count': sum(1 for e in deduped if e['inert_503']),
        'by_feature': dict(sorted(by_feature.items())),
        'mutating_by_feature': dict(sorted(by_feature_mut.items())),
        'endpoints': deduped,
    }


# ----------------------------- TRACK D -----------------------------

# Feature crosswalk: builds correlation between FE routes, FE callsites,
# BE endpoints by feature keyword.

def build_feature_crosswalk(fe_routes: dict, fe_calls: dict, be_endpoints: dict) -> dict:
    features = sorted({
        'heroes', 'collection', 'encyclopedia', 'training',
        'gacha', 'summon',
        'artifact', 'constellation',
        'shop', 'item-shop', 'economy', 'treasury', 'vip',
        'battlepass',
        'equipment', 'forge', 'exclusive', 'divine-weapons',
        'server-profile', 'servers',
        'housing',
        'status-codex', 'codex',
        'hero-skill-kits',
        'daily-hub', 'events', 'achievements', 'mail',
        'pvp', 'arena', 'story', 'tower', 'raid', 'guild', 'gvg', 'territory',
        'safe-previews',
        'inventory',
        'auth', 'login',
        'social', 'friends', 'chat', 'dm',
        'admin', 'dev', 'qa',
        'affinity',
        'soul-forge',
    })
    cw: list[dict] = []
    for feat in features:
        fe_routes_for = [r['route'] for r in fe_routes['routes']
                         if feat.replace('-', '') in r['route'].lower().replace('-', '')]
        fe_calls_for = [c for c in fe_calls['callsites']
                        if feat.replace('-', '') in c['endpoint'].lower().replace('-', '')]
        be_for = [e for e in be_endpoints['endpoints']
                  if feat.replace('-', '') in e['path'].lower().replace('-', '')]
        cw.append({
            'feature': feat,
            'frontend_routes': sorted(set(fe_routes_for)),
            'frontend_callsites_count': len(fe_calls_for),
            'frontend_mutating_callsites': sum(1 for c in fe_calls_for if c['mutating']),
            'backend_endpoints_count': len(be_for),
            'backend_mutating_endpoints': sum(1 for e in be_for if e['mutating']),
            'backend_inert_503': sum(1 for e in be_for if e['inert_503']),
        })
    # detect duplications: features with multiple FE routes
    dups = [c for c in cw if len(c['frontend_routes']) > 1]
    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'D',
        'verdict': 'TRACK_D_FEATURE_MODE_CROSSWALK_AND_DUPLICATION_AUDIT_READY',
        'feature_count': len(cw),
        'duplicate_feature_routes': [
            {'feature': d['feature'], 'routes': d['frontend_routes']}
            for d in dups
        ],
        'crosswalk': cw,
    }


# ----------------------------- TRACK E -----------------------------

def build_economy_risk_audit(fe_calls: dict, be_endpoints: dict) -> dict:
    high_risk_endpoints = [
        e for e in be_endpoints['endpoints']
        if e['risk'] == 'high'
        and e['feature'] in ('gacha', 'artifact', 'constellation', 'shop',
                             'battlepass', 'battle_pass', 'vip', 'hero',
                             'equipment', 'forge', 'exclusive', 'soul',
                             'affinity', 'inventory')
    ]
    iap_present = any('iap' in e['path'].lower()
                       or 'receipt' in e['path'].lower()
                       or 'store-kit' in e['path'].lower()
                       or 'play-billing' in e['path'].lower()
                       for e in be_endpoints['endpoints'])
    risks: list[dict] = []
    # gacha rates premium 30%
    risks.append({
        'id': 'GACHA-PREMIUM-RATES',
        'severity': 'high',
        'observation': 'Premium/Targeted gacha banners expose combined 5*+6* >= 30% (dev/test-like).',
        'evidence': ['frontend/app/(tabs)/gacha.tsx', 'backend/server.py'],
    })
    risks.append({
        'id': 'ARTIFACT-LIVE-EXPOSED',
        'severity': 'critical',
        'observation': '/artifacts route exposes pull/pull10/fuse/equip live without gate.',
        'evidence': ['frontend/app/artifacts.tsx'],
    })
    risks.append({
        'id': 'SHOP-LIVE-NO-IAP',
        'severity': 'high',
        'observation': 'Shop exposes buy/claim live but no IAP backend implementation present.',
        'evidence': ['frontend/app/shop.tsx', 'frontend/app/item-shop.tsx'],
        'iap_backend_present': iap_present,
    })
    risks.append({
        'id': 'BATTLEPASS-PREMIUM-NO-IAP',
        'severity': 'high',
        'observation': 'Battle Pass exposes buy-premium without IAP backing.',
        'evidence': ['frontend/app/battlepass.tsx'],
    })
    risks.append({
        'id': 'VIP-SPEND-NO-IAP',
        'severity': 'high',
        'observation': 'VIP spend-based progression visible without real-money purchase backend.',
        'evidence': ['frontend/app/vip.tsx', 'frontend/app/(tabs)/menu.tsx'],
    })
    risks.append({
        'id': 'HEROES-LEGACY-VISIBILITY',
        'severity': 'medium',
        'observation': '/api/user/heroes consumed without legacy visibility filter.',
        'evidence': ['frontend/app/(tabs)/heroes.tsx', 'frontend/app/hero-collection.tsx'],
    })
    risks.append({
        'id': 'EXCLUSIVE-ITEMS-ROLE',
        'severity': 'medium',
        'observation': 'Exclusive Items role unclear (live/legacy/event reward path).',
        'evidence': ['frontend/app/exclusive.tsx'],
    })
    risks.append({
        'id': 'SOUL-FORGE-PERMANENT-DESTRUCTION',
        'severity': 'high',
        'observation': 'Soul forge may permanently destroy heroes if exposed live.',
        'evidence': ['frontend/app/soul-forge.tsx'],
    })
    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'E',
        'verdict': 'TRACK_E_ECONOMY_MONETIZATION_GACHA_ROSTER_RISK_AUDIT_READY',
        'iap_backend_present': iap_present,
        'high_risk_backend_endpoint_count': len(high_risk_endpoints),
        'risks': risks,
        'high_risk_backend_endpoints': sorted(
            [{'path': e['path'], 'method': e['method'], 'file': e['file'],
              'feature': e['feature']} for e in high_risk_endpoints],
            key=lambda x: (x['feature'], x['path'])
        ),
    }


# ----------------------------- TRACK F -----------------------------

def build_gates_dev_audit(fe_routes: dict, be_endpoints: dict) -> dict:
    locked_previews = [
        r['route'] for r in fe_routes['routes']
        if 'LOCKED_PREVIEW' in r['flags']
    ]
    dev_screens = [r['route'] for r in fe_routes['routes']
                   if 'DEV_ONLY' in r['flags']]
    legacy_live = [r['route'] for r in fe_routes['routes']
                   if 'LEGACY_LIVE_MUTATION' in r['flags']]
    inert_eps = [e['path'] for e in be_endpoints['endpoints']
                 if e['inert_503']]
    gate_findings = [
        {
            'id': 'GATE-SERVER-PROFILES',
            'status': 'CORRECT_LOCKED_PREVIEW',
            'observation': '/api/server-profiles/select returns 503 inert.',
        },
        {
            'id': 'GATE-HOUSING',
            'status': 'CORRECT_LOCKED_PREVIEW',
            'observation': '/housing-preview safe; live bonuses not active.',
        },
        {
            'id': 'GATE-ARTIFACT-LIVE',
            'status': 'INCORRECTLY_LIVE',
            'observation': '/artifacts live endpoints exposed without gate.',
        },
        {
            'id': 'GATE-AF2-N',
            'status': 'CORRECT_GATED',
            'observation': 'AF2-N canary status endpoint controls runtime via feature flag.',
        },
        {
            'id': 'GATE-STATUS-FIRST-SLICE',
            'status': 'CORRECT_LOCKED_PREVIEW',
            'observation': 'Status first-slice prod rollout blocked pending signatures.',
        },
        {
            'id': 'DEV-EXPOSURE-MENU',
            'status': 'INCORRECTLY_EXPOSED_IN_MENU',
            'observation': '/sprite-test, /dev-combat-qa-lab visible from player menu.',
        },
    ]
    return {
        'task_id': 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT',
        'track': 'F',
        'verdict': 'TRACK_F_GATES_LOCKED_PREVIEW_AND_DEV_SURFACE_AUDIT_READY',
        'locked_previews': sorted(set(locked_previews)),
        'dev_screens': sorted(set(dev_screens)),
        'legacy_live_routes': sorted(set(legacy_live)),
        'inert_503_endpoints': sorted(set(inert_eps)),
        'gate_findings': gate_findings,
    }


# ----------------------------- main --------------------------------

def main() -> int:
    a = build_frontend_route_menu_registry()
    b = build_frontend_api_callsite_registry()
    c = build_backend_endpoint_registry()
    d = build_feature_crosswalk(a, b, c)
    e = build_economy_risk_audit(b, c)
    f = build_gates_dev_audit(a, c)

    out_map = {
        'frontend_route_menu_registry_v1.json': a,
        'frontend_api_callsite_registry_v1.json': b,
        'backend_endpoint_mutation_registry_v1.json': c,
        'feature_mode_crosswalk_v1.json': d,
        'economy_gacha_roster_risk_audit_v1.json': e,
        'gates_locked_preview_dev_surface_audit_v1.json': f,
    }
    for name, payload in out_map.items():
        (OUT_DIR / name).write_text(
            json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + '\n',
            encoding='utf-8'
        )
        print(f'[OK] wrote {name}')
    print('[DONE] scanner complete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
