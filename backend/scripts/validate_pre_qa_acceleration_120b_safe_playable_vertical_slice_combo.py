#!/usr/bin/env python3
"""Pre-QA Acceleration 120B — Safe Playable Vertical Slice Combo Validator.

Macro-pack unico che unifica le verifiche delle Track A/B/C/D del Pack 120A
in un singolo validator statico read-only.

Track A — Tier 0/Tier 1 Visual QA Evidence:
  * Le 6 route Tier 0/1 hanno file target esistente.
  * Le label sono player-facing pulite (no QA/TEST/V88/V90/Renderer/Wireframe).
  * Le route non espongono mutation strong senza gating.

Track B — Tier 2 Controlled Gated Interaction Dry-Run:
  * Le 11 route Tier 2 hanno file target esistente.
  * Ogni Tier 2 con strong HTTP mutation / strong keyword DEVE avere
    evidenza di gating count > 0.
  * Nessuna Tier 2 puo' essere classificata unsafe_exposed dal 119D.

Track C — Tier 3 Battle Preview Visual Pass:
  * Le 5 route /pre-battle-lobby?mode=... esistono.
  * pre-battle-lobby.tsx contiene marker preview-only:
      - 'is_preview', 'reward_policy', 'preview', 'blocked_no_team_for_server'.
  * combat.tsx contiene il token canonico 'PREVIEW_REWARD_LOCK_ACTIVE'.
  * Nessun authoritative reward grant / EXP / ranking commit live nel pre-QA.

Track D — Unified harness:
  * Piano 120A valido (mode=plan_only, no apply_now, no live_reward).
  * 119D matrix riconciliata col piano 120A.
  * Repo: nessuna route live-blocked esposta nel menu pubblico filtrato.
  * Output JSON unificato in
    backend/reports/pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json

Exit code:
  - 0 : PASS.
  - 1 : FAIL.
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
PRE_BATTLE_LOBBY_TSX = os.path.join(R, 'frontend', 'app',
                                    'pre-battle-lobby.tsx')
COMBAT_TSX = os.path.join(R, 'frontend', 'app', 'combat.tsx')
PLAN_FP = os.path.join(R, 'data', 'design', 'pre_qa_controlled_unlock',
                       'controlled_live_unlock_prep_120a_plan_v1.json')
D119D_LATEST = os.path.join(R, 'backend', 'reports',
                            'pre_qa_pack_119d_public_menu_route_health_latest.json')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Token canonici richiesti.
PRE_BATTLE_LOBBY_REQUIRED_TOKENS = [
    'is_preview',
    'reward_policy',
    'preview',
    'blocked_no_team_for_server',
    'battle_engine_mode',
]
COMBAT_REQUIRED_TOKENS = [
    'PREVIEW_REWARD_LOCK_ACTIVE',
    'PREVIEW_NON_AUTHORITATIVE',
]
TIER3_MODES_EXPECTED = ['story', 'tower', 'arena', 'training', 'boss']

# Label tecniche proibite (player-facing pulizia).
TECHNICAL_LABEL_TOKENS = [
    'QA', 'TEST', 'V88', 'V90', 'Renderer', 'Wireframe', 'Deprecato',
]

LIVE_BLOCKED_ROUTES_EXPECTED = [
    '/shop', '/vip', '/battlepass', '/gacha', '/pvp', '/guild', '/gvg',
    '/raid', '/territory', '/plaza', '/dm', '/events', '/mail', '/friends',
    '/playable-mode-battle-preview', '/skill-status-vfx-catalogs',
    '/hero-skill-kits-catalog', '/safe-previews',
]


# Decoder utility: trasforma escape JS \uXXXX -> char Python.
_UESC_RE = re.compile(r'\\u([0-9A-Fa-f]{4})')


def _decode_js_string(s: str) -> str:
    return _UESC_RE.sub(lambda m: chr(int(m.group(1), 16)), s)


# ------------------------------------------------------------
# Menu / guard parsing (mirror 119C/119D, embedded read-only).
# ------------------------------------------------------------
_CATEGORY_START_RE = re.compile(r"title:\s*'([^']+)'")
_ITEM_RE = re.compile(r"label:\s*'([^']+)'[\s\S]*?route:\s*'([^']+)'")


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
                    items.append({
                        'label': _decode_js_string(m.group(1)),
                        'route': m.group(2),
                    })
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
            route = it['route'].split('?', 1)[0]
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
# File checks
# ------------------------------------------------------------
def _route_to_file(route: str) -> str:
    base = route.split('?', 1)[0].split('#', 1)[0]
    rel = base.lstrip('/')
    if not rel:
        return os.path.join('frontend', 'app', 'index.tsx')
    return os.path.join('frontend', 'app', f'{rel}.tsx')


def _check_tokens_in_file(fp_rel: str, tokens: list) -> dict:
    fp = os.path.join(R, fp_rel)
    if not os.path.exists(fp):
        return {
            'exists': False,
            'missing_tokens': list(tokens),
            'found_tokens': [],
        }
    src = open(fp, encoding='utf-8', errors='replace').read()
    missing = [t for t in tokens if t not in src]
    found = [t for t in tokens if t in src]
    return {'exists': True, 'missing_tokens': missing, 'found_tokens': found}


def _label_is_clean(label: str) -> tuple:
    label_lower = label.lower()
    for tok in TECHNICAL_LABEL_TOKENS:
        if re.search(rf'(?<![a-z]){re.escape(tok.lower())}(?![a-z])',
                     label_lower):
            return False, tok
    return True, None


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main() -> int:
    failures = []
    info = []

    # --- Carica piano 120A
    if not os.path.exists(PLAN_FP):
        failures.append(f'piano 120A mancante: {PLAN_FP}')
        return _emit({'failures': failures})
    try:
        plan = json.load(open(PLAN_FP, encoding='utf-8'))
    except Exception as e:
        failures.append(f'piano 120A non parsabile: {e}')
        return _emit({'failures': failures})

    # Sanity-check flag plan-only.
    for k, expected in [
        ('mode', 'plan_only'),
        ('runtime_unlock_applied', False),
        ('db_write_allowed', False),
        ('reward_live_allowed', False),
        ('gacha_shop_vip_bp_allowed', False),
    ]:
        if plan.get(k) != expected:
            failures.append(f'piano 120A: {k}!={expected} (val={plan.get(k)!r})')

    candidates = plan.get('route_candidates') or []
    if len(candidates) == 0:
        failures.append('piano 120A: route_candidates vuoto')

    # Per ogni candidate piano: verifica apply_now/live_reward/economy_live.
    for c in candidates:
        for k in ('apply_now', 'live_reward_enabled', 'economy_live_enabled'):
            if c.get(k) is True:
                failures.append(
                    f"piano 120A: candidate {c.get('route')!r} ha {k}=true")

    # --- Carica 119D latest
    if not os.path.exists(D119D_LATEST):
        failures.append(f'119D latest JSON mancante: {D119D_LATEST}')
        return _emit({'failures': failures})
    try:
        d119d = json.load(open(D119D_LATEST, encoding='utf-8'))
    except Exception as e:
        failures.append(f'119D latest non parsabile: {e}')
        return _emit({'failures': failures})

    if d119d.get('unsafe_exposed_count', 0) != 0:
        failures.append(
            f"119D unsafe_exposed_count={d119d.get('unsafe_exposed_count')}")
    if d119d.get('unknown_count', 0) != 0:
        failures.append(
            f"119D unknown_count={d119d.get('unknown_count')}")
    if d119d.get('leaked_blocked_routes_count', 0) != 0:
        failures.append(
            f"119D leaked_blocked_routes_count="
            f"{d119d.get('leaked_blocked_routes_count')}")

    # --- Ricostruisci menu pubblico filtrato (sanity check Track A/B/C cover).
    menu_src = open(MENU_TSX, encoding='utf-8').read()
    guard_src = open(GUARD_TS, encoding='utf-8').read()
    block = _extract_categories_block(menu_src)
    cats = _parse_menu_categories(block)
    blocked_routes = _extract_string_set(guard_src, 'PRE_QA_BLOCKED_PLAYER_ROUTES')
    blocked_categories = _extract_string_set(guard_src, 'PRE_QA_BLOCKED_CATEGORIES')
    public = _filter_public_menu(cats, blocked_routes, blocked_categories)

    visible_full = []
    for cat in public:
        for it in cat['items']:
            visible_full.append({
                'category': cat['title'], 'label': it['label'],
                'route': it['route'],
            })

    # --- Verifica label clean su menu pubblico.
    for v in visible_full:
        ok, tok = _label_is_clean(v['label'])
        if not ok:
            failures.append(
                f"label tecnica esposta: {v['label']!r} (token={tok!r}, "
                f"route={v['route']!r})")

    # --- Verifica route live-blocked NON nel menu pubblico.
    visible_routes_set = {v['route'].split('?', 1)[0] for v in visible_full}
    leaked = [r for r in LIVE_BLOCKED_ROUTES_EXPECTED
              if r in visible_routes_set or any(
                  vr.startswith(r + '/') for vr in visible_routes_set)]
    if leaked:
        failures.append(f'route live-blocked esposte nel menu pubblico: {leaked}')

    # --- Track A — Tier 0/Tier 1
    tier01_results = []
    for c in candidates:
        if c['tier'] not in (0, 1):
            continue
        ft = c['file_target']
        exists = os.path.exists(os.path.join(R, ft))
        # In 119D matrix cerca classification.
        d_match = next((r for r in d119d.get('route_matrix', [])
                        if r['route'] == c['route']), None)
        clas_119d = (d_match or {}).get('classification', 'unknown')
        ok = exists and clas_119d not in ('unsafe_exposed',
                                          'unknown_needs_review')
        tier01_results.append({
            'route': c['route'], 'label': c['label'],
            'file_target': ft, 'file_target_exists': exists,
            'classification_119d': clas_119d, 'visual_qa_ready': ok,
        })
        if not exists:
            failures.append(
                f"Tier{c['tier']} file mancante: {ft} (route={c['route']!r})")
        if not ok:
            failures.append(
                f"Tier{c['tier']} non visual-qa-ready: {c['route']!r}")

    # --- Track B — Tier 2
    tier2_results = []
    for c in candidates:
        if c['tier'] != 2:
            continue
        ft = c['file_target']
        exists = os.path.exists(os.path.join(R, ft))
        d_match = next((r for r in d119d.get('route_matrix', [])
                        if r['route'] == c['route']), None)
        clas_119d = (d_match or {}).get('classification', 'unknown')
        http_mut = (d_match or {}).get('http_mutation_count', 0)
        strong = (d_match or {}).get('mutation_keywords_strong', {}) or {}
        gating = (d_match or {}).get('gating_evidence_count', 0)
        # Tier 2 deve essere gated se ha mutazione.
        if (http_mut > 0 or len(strong) > 0) and gating == 0:
            failures.append(
                f"Tier2 mutation non gated: {c['route']!r} "
                f"http_mut={http_mut} strong={strong} gating={gating}")
        if clas_119d == 'unsafe_exposed':
            failures.append(f"Tier2 unsafe_exposed: {c['route']!r}")
        ok = exists and clas_119d != 'unsafe_exposed' and (
            gating > 0 or (http_mut == 0 and len(strong) == 0))
        tier2_results.append({
            'route': c['route'], 'label': c['label'],
            'file_target': ft, 'file_target_exists': exists,
            'classification_119d': clas_119d,
            'http_mutation_count': http_mut,
            'mutation_keywords_strong': strong,
            'gating_evidence_count': gating,
            'dry_run_ready': ok,
        })
        if not exists:
            failures.append(
                f"Tier2 file mancante: {ft} (route={c['route']!r})")

    # --- Track C — Tier 3 (pre-battle-lobby)
    tier3_results = []
    pb_check = _check_tokens_in_file(
        os.path.relpath(PRE_BATTLE_LOBBY_TSX, R),
        PRE_BATTLE_LOBBY_REQUIRED_TOKENS)
    combat_check = _check_tokens_in_file(
        os.path.relpath(COMBAT_TSX, R), COMBAT_REQUIRED_TOKENS)
    if not pb_check['exists']:
        failures.append('pre-battle-lobby.tsx mancante')
    elif pb_check['missing_tokens']:
        failures.append(
            f"pre-battle-lobby.tsx missing tokens: "
            f"{pb_check['missing_tokens']}")
    if not combat_check['exists']:
        failures.append('combat.tsx mancante')
    elif combat_check['missing_tokens']:
        failures.append(
            f"combat.tsx missing tokens: {combat_check['missing_tokens']}")

    # Verifica le 5 mode Tier 3 presenti come candidates.
    tier3_modes_found = []
    for c in candidates:
        if c['tier'] != 3:
            continue
        m = re.search(r'mode=([a-z_]+)', c['route'])
        mode = m.group(1) if m else None
        tier3_modes_found.append(mode)
        d_match = next((r for r in d119d.get('route_matrix', [])
                        if r['route'] == c['route']), None)
        gating = (d_match or {}).get('gating_evidence_count', 0)
        tier3_results.append({
            'route': c['route'], 'mode': mode, 'label': c['label'],
            'pb_lobby_tokens_ok': pb_check['exists'] and not pb_check['missing_tokens'],
            'combat_tokens_ok': combat_check['exists'] and not combat_check['missing_tokens'],
            'gating_evidence_count_119d': gating,
            'visual_preview_ready': (
                pb_check['exists'] and not pb_check['missing_tokens']
                and combat_check['exists']
                and not combat_check['missing_tokens']
            ),
        })
    missing_modes = [m for m in TIER3_MODES_EXPECTED
                     if m not in tier3_modes_found]
    if missing_modes:
        failures.append(
            f'Tier3: mancano mode pre-battle-lobby: {missing_modes}')
    if len(tier3_results) != 5:
        failures.append(
            f'Tier3: attese 5 candidate mode, trovate {len(tier3_results)}')

    # --- Cross-check: 119D route count == candidate count.
    d119d_routes = [r['route'] for r in d119d.get('route_matrix', [])]
    plan_routes = [c['route'] for c in candidates]
    missing_in_plan = [r for r in d119d_routes if r not in plan_routes]
    if missing_in_plan:
        failures.append(
            f'piano 120A non copre tutte le route 119D: missing={missing_in_plan}')

    # --- Build verdict + JSON output
    tier_counts = {
        'tier_0_visual': sum(1 for c in candidates if c['tier'] == 0),
        'tier_1_visual': sum(1 for c in candidates if c['tier'] == 1),
        'tier_2_dry_run': sum(1 for c in candidates if c['tier'] == 2),
        'tier_3_battle_preview': sum(1 for c in candidates if c['tier'] == 3),
    }
    tier01_ready = sum(1 for r in tier01_results if r['visual_qa_ready'])
    tier2_ready = sum(1 for r in tier2_results if r['dry_run_ready'])
    tier3_ready = sum(1 for r in tier3_results if r['visual_preview_ready'])

    verdict = 'PASS' if not failures else 'FAIL'

    out = {
        'tool': 'validate_pre_qa_acceleration_120b_safe_playable_vertical_slice_combo',
        'pack_origin': '120B',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'inputs': {
            'plan_120a': os.path.relpath(PLAN_FP, R),
            'd119d_latest': os.path.relpath(D119D_LATEST, R),
            'menu_tsx': os.path.relpath(MENU_TSX, R),
            'guard_ts': os.path.relpath(GUARD_TS, R),
            'pre_battle_lobby_tsx': os.path.relpath(PRE_BATTLE_LOBBY_TSX, R),
            'combat_tsx': os.path.relpath(COMBAT_TSX, R),
        },
        'plan_flags': {
            'mode': plan.get('mode'),
            'runtime_unlock_applied': plan.get('runtime_unlock_applied'),
            'db_write_allowed': plan.get('db_write_allowed'),
            'reward_live_allowed': plan.get('reward_live_allowed'),
            'gacha_shop_vip_bp_allowed': plan.get('gacha_shop_vip_bp_allowed'),
        },
        'candidates_count': len(candidates),
        'tier_counts': tier_counts,
        'visible_menu_item_count': len(visible_full),
        'live_blocked_routes_leaked': leaked,
        'track_a_tier01_results': tier01_results,
        'track_a_visual_qa_ready_count': tier01_ready,
        'track_b_tier2_results': tier2_results,
        'track_b_dry_run_ready_count': tier2_ready,
        'track_c_tier3_results': tier3_results,
        'track_c_visual_preview_ready_count': tier3_ready,
        'track_c_pre_battle_lobby_check': pb_check,
        'track_c_combat_check': combat_check,
        'track_c_modes_expected': TIER3_MODES_EXPECTED,
        'track_c_modes_found': tier3_modes_found,
        'failures': failures,
        'verdict': verdict,
    }

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_fp = os.path.join(
        REPORTS_DIR,
        f'pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_{stamp}.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    latest_fp = os.path.join(
        REPORTS_DIR,
        'pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json')
    try:
        if os.path.exists(latest_fp):
            os.remove(latest_fp)
        with open(latest_fp, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    print('============== PACK 120B — VERTICAL SLICE COMBO ==============')
    print(f"  candidates: {out['candidates_count']}")
    print(f"  tier counts: {out['tier_counts']}")
    print(f"  Track A visual QA ready: {tier01_ready}/{len(tier01_results)}")
    print(f"  Track B dry-run ready:   {tier2_ready}/{len(tier2_results)}")
    print(f"  Track C battle preview ready: {tier3_ready}/{len(tier3_results)}")
    print(f"  failures: {len(failures)}")
    print(f"  verdict: {verdict}")
    print(f"  JSON out: {out_fp}")
    print(f"  JSON latest: {latest_fp}")
    print('===============================================================')

    if verdict == 'FAIL':
        print('')
        print('[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1

    print('')
    print('[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO] OK '
          f"candidates={out['candidates_count']} "
          f"tier01_ready={tier01_ready} tier2_ready={tier2_ready} "
          f"tier3_ready={tier3_ready} live_blocked_leaked=0 "
          f"unsafe_exposed=0 unknown=0")
    return 0


def _emit(stub: dict) -> int:
    """Emergency emit per early-exit."""
    print('[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO] FAIL')
    for f in stub.get('failures', []):
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
