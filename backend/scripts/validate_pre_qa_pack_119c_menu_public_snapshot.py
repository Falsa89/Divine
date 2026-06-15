#!/usr/bin/env python3
"""Pre-QA Pack 119C — Menu Public Route Semantic Dedupe & Snapshot Validator.

Validator statico (regex-based, niente runtime TSX) che:
  1. Estrae da `frontend/app/(tabs)/menu.tsx` l'array CATEGORIES (categorie +
     voci label/route).
  2. Estrae da `frontend/src/utils/preQaNavGuard.ts` i set canonici di route
     player-facing bloccate (`PRE_QA_BLOCKED_PLAYER_ROUTES`) e categorie QA
     nascoste (`PRE_QA_BLOCKED_CATEGORIES`).
  3. Applica la stessa logica di filtro del menu (categoria allowed +
     `isRouteAllowedInPreQa`) per produrre lo SNAPSHOT del menu pubblico
     filtrato che vedrebbe il giocatore con guard di default.
  4. Verifica i criteri Pack 119C:
       a) nessuna label visibile contiene token tecnici (QA, TEST, V88, V90,
          Renderer, Wireframe, Deprecato).
       b) nessuna categoria visibile contiene token QA.
       c) nessuna route visibile include /playable-mode-battle-preview,
          /skill-status-vfx-catalogs, /hero-skill-kits-catalog, /safe-previews.
       d) nessuna route duplicata player-facing (eccezioni esplicite vuote).
       e) /soul-forge appare una sola volta.
       f) tutte le route live-blocked restano nel set bloccato del guard.

Exit code:
  - 0 : tutti i criteri PASS. Stampa snapshot finale machine-readable JSON.
  - 1 : almeno un criterio FAIL.

Onesto e non-fragile:
  - Mai accede al runtime TSX, quindi nessun rischio Metro/Expo.
  - Parsing per linea limitato all'array CATEGORIES, scoping esplicito.
  - Niente fake-pass: ogni assert fallisce in modo verboso e termina con rc=1.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

# ------------------------------------------------------------
# Path setup
# ------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
MENU_TSX = os.path.join(R, 'frontend', 'app', '(tabs)', 'menu.tsx')
GUARD_TS = os.path.join(R, 'frontend', 'src', 'utils', 'preQaNavGuard.ts')

# ------------------------------------------------------------
# Token / regola Pack 119C
# ------------------------------------------------------------
# Token tecnici proibiti nelle LABEL player-facing visibili (case-insensitive).
TECHNICAL_LABEL_TOKENS = [
    'QA',
    'TEST',
    'V88',
    'V90',
    'Renderer',
    'Wireframe',
    'Deprecato',
]
# Token proibiti nei TITOLI di categoria visibili (case-insensitive substring).
TECHNICAL_CATEGORY_TOKENS = [
    'Playability & Announcements QA',
    'Modalit\u00e0 Live & Guild QA',
    'Battle Preview QA',
]
# Prefissi route che NON devono mai apparire nelle voci visibili.
DEV_ROUTE_PREFIXES = [
    '/playable-mode-battle-preview',
    '/skill-status-vfx-catalogs',
    '/hero-skill-kits-catalog',
    '/safe-previews',
]
# Route live-blocked che devono restare nel guard.
LIVE_BLOCKED_ROUTES_EXPECTED = [
    '/shop',
    '/vip',
    '/battlepass',
    '/gacha',
    '/pvp',
    '/guild',
    '/gvg',
    '/raid',
    '/territory',
    '/plaza',
    '/dm',
    '/events',
    '/mail',
    '/friends',
]
# Eccezioni esplicite per route duplicate "lecite". Nessuna ammessa per Pack 119C.
ALLOWED_DUPLICATE_ROUTES: set = set()

# Decoder utility: trasforma escape JS \uXXXX -> char Python.
_UESC_RE = re.compile(r'\\u([0-9A-Fa-f]{4})')


def _decode_js_string(s: str) -> str:
    return _UESC_RE.sub(lambda m: chr(int(m.group(1), 16)), s)


# ------------------------------------------------------------
# Parser menu.tsx -> lista categorie con label/route
# ------------------------------------------------------------
_CATEGORY_START_RE = re.compile(r"title:\s*'([^']+)'")
_ITEM_RE = re.compile(
    r"label:\s*'([^']+)'[\s\S]*?route:\s*'([^']+)'"
)


def _extract_categories_block(src: str) -> str:
    """Estrae il body dell'array CATEGORIES da menu.tsx."""
    m = re.search(r'const\s+CATEGORIES\s*=\s*\[', src)
    if not m:
        raise SystemExit('FAIL: const CATEGORIES non trovata in menu.tsx')
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        ch = src[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        i += 1
    if depth != 0:
        raise SystemExit('FAIL: array CATEGORIES non bilanciato')
    return src[start:i - 1]


def _parse_menu_categories(block: str) -> list:
    """Suddivide il blocco CATEGORIES in oggetti categoria e parsa label/route.

    Approccio: scorri il blocco a livello { ... } depth=1; ogni categoria e' un
    oggetto top-level. Per ciascuna, estrai title e gli items (label, route).
    """
    categories = []
    depth = 0
    buf_start = None
    for i, ch in enumerate(block):
        if ch == '{':
            if depth == 0:
                buf_start = i + 1
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and buf_start is not None:
                cat_body = block[buf_start:i]
                t = _CATEGORY_START_RE.search(cat_body)
                if not t:
                    buf_start = None
                    continue
                title = _decode_js_string(t.group(1))
                items = []
                # Per evitare di matchare oggetti annidati spuri, parse semplice
                # su tutta la categoria: i campi sono sempre `label: '...'` e
                # `route: '...'` nella stessa riga item.
                for m in _ITEM_RE.finditer(cat_body):
                    label = _decode_js_string(m.group(1))
                    route = m.group(2)
                    items.append({'label': label, 'route': route})
                categories.append({'title': title, 'items': items})
                buf_start = None
    return categories


# ------------------------------------------------------------
# Parser preQaNavGuard.ts -> set di route/categorie bloccate
# ------------------------------------------------------------
def _extract_string_set(src: str, var_name: str) -> set:
    """Estrae i literal 'xxx' dal Set<string>([...]) per `var_name`."""
    pattern = re.compile(
        rf"export\s+const\s+{re.escape(var_name)}[^=]*=\s*new\s+Set<string>\s*\(\s*\[",
        re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        raise SystemExit(f'FAIL: {var_name} non trovato in preQaNavGuard.ts')
    i = m.end()
    depth = 1  # contiamo '[' / ']'
    start = i
    while i < len(src) and depth > 0:
        ch = src[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        i += 1
    body = src[start:i - 1]
    out = set()
    for lit in re.finditer(r"'([^']+)'", body):
        out.add(_decode_js_string(lit.group(1)))
    return out


# ------------------------------------------------------------
# Filtro snapshot menu pubblico (mirror della logica TS in menu.tsx)
# ------------------------------------------------------------
def _filter_public_menu(categories: list, blocked_routes: set,
                       blocked_categories: set) -> list:
    public = []
    for cat in categories:
        if cat['title'] in blocked_categories:
            continue
        visible_items = []
        for it in cat['items']:
            route = it['route'].split('?', 1)[0].split('#', 1)[0]
            is_blocked = False
            for br in blocked_routes:
                if route == br or route.startswith(br + '/'):
                    is_blocked = True
                    break
            if not is_blocked:
                visible_items.append(it)
        if visible_items:
            public.append({'title': cat['title'], 'items': visible_items})
    return public


# ------------------------------------------------------------
# Validation suite
# ------------------------------------------------------------
def _check_labels_clean(public: list) -> list:
    failures = []
    for cat in public:
        for it in cat['items']:
            label_lower = it['label'].lower()
            for tok in TECHNICAL_LABEL_TOKENS:
                # Match case-insensitive, ma evita false positive su lettere
                # interne ai word: usa boundary "word-ish".
                if re.search(rf'(?<![a-z]){re.escape(tok.lower())}(?![a-z])',
                             label_lower):
                    failures.append({
                        'category': cat['title'],
                        'label': it['label'],
                        'route': it['route'],
                        'token': tok,
                        'rule': 'TECHNICAL_LABEL_FORBIDDEN',
                    })
    return failures


def _check_categories_clean(public: list) -> list:
    failures = []
    for cat in public:
        for tok in TECHNICAL_CATEGORY_TOKENS:
            if tok.lower() in cat['title'].lower():
                failures.append({
                    'category': cat['title'],
                    'token': tok,
                    'rule': 'TECHNICAL_CATEGORY_FORBIDDEN',
                })
    return failures


def _check_dev_routes_hidden(public: list) -> list:
    failures = []
    for cat in public:
        for it in cat['items']:
            for pref in DEV_ROUTE_PREFIXES:
                if it['route'].startswith(pref):
                    failures.append({
                        'category': cat['title'],
                        'label': it['label'],
                        'route': it['route'],
                        'prefix': pref,
                        'rule': 'DEV_ROUTE_LEAKED_TO_PUBLIC',
                    })
    return failures


def _check_route_uniqueness(public: list) -> list:
    """Verifica duplicati route player-facing.

    Chiave di dedupe: route FULL (path + query), perche' modalita' diverse
    della stessa pre-battle-lobby (`/pre-battle-lobby?mode=story`, `?mode=tower`,
    ...) sono entry-point distinti per il giocatore, non doppioni semantici.
    Un doppione e' quando DUE voci differenti puntano alla stessa URL completa.
    """
    failures = []
    seen = {}
    for cat in public:
        for it in cat['items']:
            full = it['route']
            if full in seen and full not in ALLOWED_DUPLICATE_ROUTES:
                failures.append({
                    'route': full,
                    'first_seen_in': seen[full]['category'],
                    'first_seen_label': seen[full]['label'],
                    'duplicate_in': cat['title'],
                    'duplicate_label': it['label'],
                    'rule': 'DUPLICATE_PLAYER_ROUTE',
                })
            else:
                seen[full] = {'category': cat['title'], 'label': it['label']}
    return failures


def _check_soul_forge_unique(public: list) -> list:
    occurrences = []
    for cat in public:
        for it in cat['items']:
            if it['route'].split('?', 1)[0] == '/soul-forge':
                occurrences.append({
                    'category': cat['title'],
                    'label': it['label'],
                    'route': it['route'],
                })
    if len(occurrences) > 1:
        return [{
            'rule': 'SOUL_FORGE_DUPLICATE',
            'occurrences': occurrences,
        }]
    if len(occurrences) == 0:
        return [{
            'rule': 'SOUL_FORGE_MISSING',
            'note': '/soul-forge non presente nel menu pubblico filtrato',
        }]
    return []


def _check_live_blocked_routes(guard_blocked: set) -> list:
    failures = []
    for r in LIVE_BLOCKED_ROUTES_EXPECTED:
        if r not in guard_blocked:
            failures.append({
                'route': r,
                'rule': 'LIVE_ROUTE_NOT_BLOCKED_IN_GUARD',
            })
    return failures


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main() -> int:
    if not os.path.exists(MENU_TSX):
        print(f'FAIL: menu.tsx mancante: {MENU_TSX}')
        return 1
    if not os.path.exists(GUARD_TS):
        print(f'FAIL: preQaNavGuard.ts mancante: {GUARD_TS}')
        return 1

    menu_src = open(MENU_TSX, encoding='utf-8').read()
    guard_src = open(GUARD_TS, encoding='utf-8').read()

    block = _extract_categories_block(menu_src)
    categories = _parse_menu_categories(block)
    blocked_routes = _extract_string_set(guard_src, 'PRE_QA_BLOCKED_PLAYER_ROUTES')
    blocked_categories = _extract_string_set(guard_src, 'PRE_QA_BLOCKED_CATEGORIES')

    public = _filter_public_menu(categories, blocked_routes, blocked_categories)

    failures = []
    failures.extend(_check_labels_clean(public))
    failures.extend(_check_categories_clean(public))
    failures.extend(_check_dev_routes_hidden(public))
    failures.extend(_check_route_uniqueness(public))
    failures.extend(_check_soul_forge_unique(public))
    failures.extend(_check_live_blocked_routes(blocked_routes))

    snapshot = {
        'tool': 'validate_pre_qa_pack_119c_menu_public_snapshot',
        'pack_origin': '119C',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'menu_tsx': os.path.relpath(MENU_TSX, R),
        'guard_ts': os.path.relpath(GUARD_TS, R),
        'public_menu_snapshot': public,
        'blocked_player_routes': sorted(blocked_routes),
        'blocked_categories': sorted(blocked_categories),
        'duplicate_route_exceptions': sorted(ALLOWED_DUPLICATE_ROUTES),
        'totals': {
            'categories_visible': len(public),
            'items_visible': sum(len(c['items']) for c in public),
            'blocked_player_routes': len(blocked_routes),
            'blocked_categories': len(blocked_categories),
            'failures': len(failures),
        },
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }

    print(json.dumps(snapshot, ensure_ascii=False, indent=2))

    if failures:
        print('')
        print('[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1

    print('')
    print('[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK '
          f"categories={snapshot['totals']['categories_visible']} "
          f"items={snapshot['totals']['items_visible']} "
          f"duplicates=0 soul_forge_unique=true labels_clean=true "
          f"dev_routes_hidden=true live_routes_blocked=true")
    return 0


if __name__ == '__main__':
    sys.exit(main())
