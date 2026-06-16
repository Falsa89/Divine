#!/usr/bin/env python3
"""Pre-QA Pack 119D — Public Menu Route Target Health & Mutation Classification.

Validator statico / read-only che:

  1. Ricostruisce il menu pubblico filtrato (stessa logica Pack 119C):
       - parsa `frontend/app/(tabs)/menu.tsx` (array CATEGORIES);
       - parsa `frontend/src/utils/preQaNavGuard.ts`
         (PRE_QA_BLOCKED_PLAYER_ROUTES + PRE_QA_BLOCKED_CATEGORIES);
       - applica filtro identico al runtime menu.
  2. Per ogni voce visibile, risolve il file target Expo Router atteso e
     verifica che esista (es. `/pre-battle-lobby?mode=story` ->
     `frontend/app/pre-battle-lobby.tsx`).
  3. Effettua un audit STATICO leggero del file target cercando:
       - chiamate HTTP mutanti (POST/PUT/PATCH/DELETE via fetch/axios/api*);
       - keyword di mutazione (claim, purchase, summon, gacha, ...);
       - segnali di gating (LOCKED, 423, preview-only, disabled, ...).
  4. Classifica ogni route in una delle classi:
       - safe_read_only
       - safe_preview_only
       - locked_deferred
       - mutation_sensitive_but_gated
       - unsafe_exposed
       - unknown_needs_review
  5. Conferma che route live/deferred (shop, vip, battlepass, gacha, pvp,
     guild, gvg, raid, territory, plaza, dm, events, mail, friends + 4 dev
     route Pack 119B) NON appaiano nel menu pubblico.

Output:
  - JSON machine-readable in `backend/reports/pre_qa_pack_119d_public_menu_route_health_<UTC>.json`
  - Linea testuale finale `[v119d ...] OK` o `[v119d ...] FAIL`.

Exit code:
  - 0 : tutti i criteri PASS (unsafe_exposed = 0, unknown_needs_review = 0,
        nessuna live route esposta, tutti i file target esistono).
  - 1 : almeno un criterio FAIL.

Non modifica DB, non avvia network, non importa runtime TSX. Parsing
regex-scoped, onesto e non fragile.
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
APP_DIR = os.path.join(R, 'frontend', 'app')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ------------------------------------------------------------
# Live route che NON devono apparire nel menu pubblico filtrato.
# ------------------------------------------------------------
LIVE_BLOCKED_ROUTES_EXPECTED = [
    '/shop', '/vip', '/battlepass', '/gacha', '/pvp', '/guild', '/gvg',
    '/raid', '/territory', '/plaza', '/dm', '/events', '/mail', '/friends',
    '/playable-mode-battle-preview',
    '/skill-status-vfx-catalogs',
    '/hero-skill-kits-catalog',
    '/safe-previews',
]

# ------------------------------------------------------------
# Pattern di mutazione HTTP "forti" (boundary-aware).
# ------------------------------------------------------------
MUTATION_HTTP_PATTERNS = [
    # axios.post(... / apiClient.post(... / api.post(... / http.post(...
    re.compile(r"\b(?:axios|apiClient|api|http|client)\s*\.\s*(?:post|put|patch|delete)\s*\(",
               re.IGNORECASE),
    # fetch(..., { method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' ... })
    re.compile(r"method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)['\"]"),
]

# Keyword di mutazione "forti" che indicano azioni live (case-insensitive,
# word boundary). Match SOLO al di fuori di commenti/stringhe contestuali
# generici e' difficile da gestire in regex; per essere onesti, contiamo
# semplicemente le occorrenze e affianchiamole all'esistenza di evidenza di
# gating per declassificare a mutation_sensitive_but_gated.
MUTATION_KEYWORDS_STRONG = [
    'claim', 'purchase', 'spend', 'redeem', 'summon', 'pullGacha',
    'gachaPull', 'subscribeVip', 'startBattle', 'startMatch',
]
MUTATION_KEYWORDS_WEAK = [
    'reward', 'buy', 'gacha', 'vip', 'battlepass', 'shop',
    'forge', 'upgrade', 'equip', 'complete', 'progress', 'ledger',
]

# Evidenza di gating / preview-only / read-only.
GATING_TOKENS = [
    'PRE_QA_ROUTE_BLOCKED',
    'PRE_QA_BLOCKED',
    'preview-only', 'preview_only',
    'read-only', 'read_only', 'READ-ONLY', 'READ_ONLY',
    'postqa_d_locked', 'postqa_locked_endpoints',
    'LOCKED', 'is_locked', 'isLocked',
    'LockedCard',
    'DEFERRED', 'deferred',
    'sandbox',
    'safe_fallback',
    'blocked_no_team_for_server',
    'CREDENTIALS_REQUIRED_FOR_STORE_BUILD',
    '423',
    'disabled=',
    'disabled\u003D',
    # Marker testuali tipici di header doc dei file stub/preview.
    'STRICT CONSTRAINTS',
    'No backend calls',
    'No state mutation',
    'No purchases',
    'No claim',
    'no claim',
    'Buttons are visually disabled',
    'visually disabled',
    'do NOT consume',
    'PROTOTYPE_FLAGS',
    'PROTOTYPE',
    'stub screen', 'Stub Screen',
    'preview, gated',
    'preview non-authoritative',
    'design-only',
    'No <Modal>',
]
# Marker espliciti di "anteprima / catalogo read-only" che spostano a
# safe_preview_only se NESSUNA mutazione e' rilevata.
PREVIEW_MARKERS = [
    'preview', 'catalog', 'placeholder', 'wireframe', 'mock',
]

# Decoder utility: trasforma escape JS \uXXXX -> char Python.
_UESC_RE = re.compile(r'\\u([0-9A-Fa-f]{4})')


def _decode_js_string(s: str) -> str:
    return _UESC_RE.sub(lambda m: chr(int(m.group(1), 16)), s)


# ------------------------------------------------------------
# Menu / guard parsing (riuso 119C, embedded per non creare dipendenze).
# ------------------------------------------------------------
_CATEGORY_START_RE = re.compile(r"title:\s*'([^']+)'")
_ITEM_RE = re.compile(
    r"label:\s*'([^']+)'[\s\S]*?route:\s*'([^']+)'"
)


def _extract_categories_block(src: str) -> str:
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
                for m in _ITEM_RE.finditer(cat_body):
                    label = _decode_js_string(m.group(1))
                    route = m.group(2)
                    items.append({'label': label, 'route': route})
                categories.append({'title': title, 'items': items})
                buf_start = None
    return categories


def _extract_string_set(src: str, var_name: str) -> set:
    pattern = re.compile(
        rf"export\s+const\s+{re.escape(var_name)}[^=]*=\s*new\s+Set<string>\s*\(\s*\[",
        re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        raise SystemExit(f'FAIL: {var_name} non trovato in preQaNavGuard.ts')
    i = m.end()
    depth = 1
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
# Route -> Expo Router file target.
# ------------------------------------------------------------
def _route_to_file(route: str) -> str:
    """Risolve route -> file relativo (relativo a R)."""
    base = route.split('?', 1)[0].split('#', 1)[0]
    if not base.startswith('/'):
        return ''
    # Strip leading '/', candidate file `frontend/app/<rel>.tsx`.
    rel = base.lstrip('/')
    if rel == '':
        return os.path.join('frontend', 'app', 'index.tsx')
    return os.path.join('frontend', 'app', f'{rel}.tsx')


# ------------------------------------------------------------
# Audit statico del file target.
# ------------------------------------------------------------
def _word_re(word: str) -> re.Pattern:
    """Costruisce un regex case-insensitive con boundary 'word-ish'."""
    return re.compile(rf'(?<![A-Za-z0-9_]){re.escape(word)}(?![A-Za-z0-9_])',
                      re.IGNORECASE)


_BLOCK_COMMENT_RE = re.compile(r'/\*[\s\S]*?\*/')
_LINE_COMMENT_RE = re.compile(r'//[^\n]*')


def _strip_js_comments(src: str) -> str:
    """Rimuove commenti // e /* */ per ridurre falsi positivi nelle keyword.

    Onesto: gli stessi commenti vengono pero' usati per cercare i token di
    gating (es. "No purchases / claim"); quindi NON modifichiamo `src` per il
    gating-scan, solo per il keyword-scan dei mutazione strong/weak.
    """
    s = _BLOCK_COMMENT_RE.sub('', src)
    s = _LINE_COMMENT_RE.sub('', s)
    return s


def _audit_file(file_rel: str) -> dict:
    fp = os.path.join(R, file_rel)
    if not os.path.exists(fp):
        return {
            'exists': False,
            'http_mutation_count': 0,
            'mutation_keywords_strong': {},
            'mutation_keywords_weak': {},
            'gating_evidence_count': 0,
            'gating_evidence_sample': [],
            'preview_marker_count': 0,
        }
    src = open(fp, encoding='utf-8', errors='replace').read()
    # Per il conteggio delle mutazioni (HTTP + keyword) usiamo il codice
    # ripulito dai commenti: questo elimina i false-positive del tipo
    # "No purchases / claim" che NON sono codice eseguibile.
    code = _strip_js_comments(src)

    http_mutation_count = 0
    for pat in MUTATION_HTTP_PATTERNS:
        http_mutation_count += len(pat.findall(code))

    strong_hits = {}
    for kw in MUTATION_KEYWORDS_STRONG:
        n = len(_word_re(kw).findall(code))
        if n > 0:
            strong_hits[kw] = n

    weak_hits = {}
    for kw in MUTATION_KEYWORDS_WEAK:
        n = len(_word_re(kw).findall(code))
        if n > 0:
            weak_hits[kw] = n

    # Gating evidence: cerchiamo nel sorgente RAW (commenti inclusi) perche'
    # tipicamente i marker "STRICT CONSTRAINTS / No claim / READ-ONLY" sono
    # nell'header doc del file.
    gating_count = 0
    gating_sample = []
    for tok in GATING_TOKENS:
        if tok in src:
            occ = src.count(tok)
            gating_count += occ
            gating_sample.append({'token': tok, 'count': occ})

    preview_count = 0
    for tok in PREVIEW_MARKERS:
        preview_count += len(_word_re(tok).findall(src))

    return {
        'exists': True,
        'http_mutation_count': http_mutation_count,
        'mutation_keywords_strong': strong_hits,
        'mutation_keywords_weak': weak_hits,
        'gating_evidence_count': gating_count,
        'gating_evidence_sample': gating_sample[:8],
        'preview_marker_count': preview_count,
    }


def _classify(audit: dict, route: str) -> dict:
    """Classifica la route in base all'audit statico.

    Logica:
      - has_strong = http_mutation_count > 0 OR mutation_keywords_strong > 0
      - has_weak   = mutation_keywords_weak  > 0
      - has_gating = gating_evidence_count > 0
      - has_preview= preview_marker_count >= 3 (multiple occorrenze pesa per
        evitare un singolo "preview" in commento)

    Tabella decisione:
      - strong  + gated   -> mutation_sensitive_but_gated
      - strong  + !gated  -> unsafe_exposed
      - !strong + weak + gated   -> mutation_sensitive_but_gated
      - !strong + weak + !gated  -> unknown_needs_review
      - !strong + !weak + gated  -> locked_deferred
      - !strong + !weak + !gated + preview -> safe_preview_only
      - !strong + !weak + !gated + !preview -> safe_read_only
    """
    if not audit['exists']:
        return {
            'classification': 'unknown_needs_review',
            'reason': 'file target missing',
            'risk_db_write': 'unknown',
            'risk_reward_claim': 'unknown',
            'risk_economy': 'unknown',
            'risk_battle_progress': 'unknown',
        }

    strong = (audit['http_mutation_count'] > 0
              or len(audit['mutation_keywords_strong']) > 0)
    weak = len(audit['mutation_keywords_weak']) > 0
    gated = audit['gating_evidence_count'] > 0
    preview = audit['preview_marker_count'] >= 3

    if strong and gated:
        cls = 'mutation_sensitive_but_gated'
        reason = ('http_mutation o strong-keyword presenti, ma file mostra '
                  'evidenza di gating (LOCKED / preview-only / 423 / disabled)')
        risk_db = 'gated'
        risk_reward = 'gated'
        risk_econ = 'gated'
        risk_battle = 'gated'
    elif strong and not gated:
        cls = 'unsafe_exposed'
        reason = ('http_mutation o strong-keyword presenti SENZA evidenza '
                  'di gating: potenziale write live esposto')
        risk_db = 'high'
        risk_reward = 'high'
        risk_econ = 'high'
        risk_battle = 'high'
    elif (not strong) and weak and gated:
        cls = 'mutation_sensitive_but_gated'
        reason = ('weak-keyword presenti + evidenza gating; nessuna chiamata '
                  'HTTP mutante diretta')
        risk_db = 'gated'
        risk_reward = 'gated'
        risk_econ = 'gated'
        risk_battle = 'gated'
    elif (not strong) and weak and not gated:
        cls = 'unknown_needs_review'
        reason = ('weak-keyword presenti senza chiare evidenze di gating; '
                  'audit umano richiesto')
        risk_db = 'unknown'
        risk_reward = 'unknown'
        risk_econ = 'unknown'
        risk_battle = 'unknown'
    elif (not strong) and (not weak) and gated:
        cls = 'locked_deferred'
        reason = 'nessuna mutazione, solo evidenza di lock/deferred'
        risk_db = 'low'
        risk_reward = 'low'
        risk_econ = 'low'
        risk_battle = 'low'
    elif (not strong) and (not weak) and (not gated) and preview:
        cls = 'safe_preview_only'
        reason = 'nessuna mutazione, marker preview/catalog ricorrenti'
        risk_db = 'none'
        risk_reward = 'none'
        risk_econ = 'none'
        risk_battle = 'none'
    else:
        cls = 'safe_read_only'
        reason = 'nessuna mutazione e nessun marker preview/lock dominante'
        risk_db = 'none'
        risk_reward = 'none'
        risk_econ = 'none'
        risk_battle = 'none'

    return {
        'classification': cls,
        'reason': reason,
        'risk_db_write': risk_db,
        'risk_reward_claim': risk_reward,
        'risk_economy': risk_econ,
        'risk_battle_progress': risk_battle,
    }


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

    route_matrix = []
    classification_counter = {
        'safe_read_only': 0,
        'safe_preview_only': 0,
        'locked_deferred': 0,
        'mutation_sensitive_but_gated': 0,
        'unsafe_exposed': 0,
        'unknown_needs_review': 0,
    }
    missing_target_routes = []

    # Dedupe per file target (per evitare di auditare 5x pre-battle-lobby).
    audit_cache = {}

    for cat in public:
        for it in cat['items']:
            route = it['route']
            file_rel = _route_to_file(route)
            if file_rel not in audit_cache:
                audit_cache[file_rel] = _audit_file(file_rel)
            audit = audit_cache[file_rel]
            verdict = _classify(audit, route)
            classification_counter[verdict['classification']] += 1
            if not audit['exists']:
                missing_target_routes.append({
                    'route': route, 'file_target': file_rel,
                    'category': cat['title'], 'label': it['label'],
                })
            route_matrix.append({
                'category': cat['title'],
                'label': it['label'],
                'route': route,
                'file_target': file_rel,
                'file_target_exists': audit['exists'],
                'http_mutation_count': audit['http_mutation_count'],
                'mutation_keywords_strong': audit['mutation_keywords_strong'],
                'mutation_keywords_weak': audit['mutation_keywords_weak'],
                'gating_evidence_count': audit['gating_evidence_count'],
                'gating_evidence_sample': audit['gating_evidence_sample'],
                'preview_marker_count': audit['preview_marker_count'],
                'classification': verdict['classification'],
                'reason': verdict['reason'],
                'risk_db_write': verdict['risk_db_write'],
                'risk_reward_claim': verdict['risk_reward_claim'],
                'risk_economy': verdict['risk_economy'],
                'risk_battle_progress': verdict['risk_battle_progress'],
            })

    # Blocked-route checks: nessuna live/dev-only route nel menu pubblico.
    visible_routes_set = set()
    for cat in public:
        for it in cat['items']:
            visible_routes_set.add(it['route'].split('?', 1)[0])
    blocked_route_checks = []
    for r in LIVE_BLOCKED_ROUTES_EXPECTED:
        leaked = r in visible_routes_set or any(
            vr.startswith(r + '/') for vr in visible_routes_set)
        blocked_route_checks.append({
            'route': r,
            'present_in_public_menu': leaked,
            'expected_blocked': True,
            'ok': not leaked,
        })

    unsafe_count = classification_counter['unsafe_exposed']
    unknown_count = classification_counter['unknown_needs_review']
    leaked_count = sum(1 for c in blocked_route_checks if not c['ok'])

    verdict = ('PASS' if (unsafe_count == 0 and unknown_count == 0
                          and leaked_count == 0
                          and not missing_target_routes)
               else 'FAIL')

    report = {
        'tool': 'validate_pre_qa_pack_119d_public_menu_route_health',
        'pack_origin': '119D',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'menu_tsx': os.path.relpath(MENU_TSX, R),
        'guard_ts': os.path.relpath(GUARD_TS, R),
        'visible_category_count': len(public),
        'visible_item_count': sum(len(c['items']) for c in public),
        'classification_counter': classification_counter,
        'missing_target_routes': missing_target_routes,
        'route_matrix': route_matrix,
        'blocked_route_checks': blocked_route_checks,
        'unsafe_exposed_count': unsafe_count,
        'unknown_count': unknown_count,
        'leaked_blocked_routes_count': leaked_count,
        'verdict': verdict,
    }

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_fp = os.path.join(REPORTS_DIR,
                          f'pre_qa_pack_119d_public_menu_route_health_{stamp}.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    latest_fp = os.path.join(
        REPORTS_DIR, 'pre_qa_pack_119d_public_menu_route_health_latest.json')
    try:
        if os.path.exists(latest_fp):
            os.remove(latest_fp)
        with open(latest_fp, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    # Human-readable summary su stdout.
    print('================ PACK 119D — ROUTE HEALTH MATRIX ================')
    print(f"  visible categories: {report['visible_category_count']}")
    print(f"  visible items:      {report['visible_item_count']}")
    print(f"  unsafe_exposed:     {unsafe_count}")
    print(f"  unknown_needs_review: {unknown_count}")
    print(f"  leaked blocked routes: {leaked_count}")
    print(f"  missing target files: {len(missing_target_routes)}")
    print('  classification counter:')
    for k, v in classification_counter.items():
        print(f"    - {k:<32} {v}")
    print(f"  JSON out: {out_fp}")
    print(f"  JSON latest: {latest_fp}")
    print(f"  verdict: {verdict}")
    print('==================================================================')

    if verdict == 'FAIL':
        print('')
        print('[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] FAIL')
        if unsafe_count > 0:
            print('  unsafe_exposed routes:')
            for r in route_matrix:
                if r['classification'] == 'unsafe_exposed':
                    print(f"    - {r['route']} ({r['label']}) [{r['file_target']}]")
        if unknown_count > 0:
            print('  unknown_needs_review routes:')
            for r in route_matrix:
                if r['classification'] == 'unknown_needs_review':
                    print(f"    - {r['route']} ({r['label']}) [{r['file_target']}]")
        if leaked_count > 0:
            print('  leaked blocked routes:')
            for c in blocked_route_checks:
                if not c['ok']:
                    print(f"    - {c['route']}")
        if missing_target_routes:
            print('  missing target files:')
            for m in missing_target_routes:
                print(f"    - {m['route']} -> {m['file_target']}")
        return 1

    print('')
    print('[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK '
          f"unsafe_exposed=0 unknown_needs_review=0 leaked=0 "
          f"file_targets_existing={report['visible_item_count']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
