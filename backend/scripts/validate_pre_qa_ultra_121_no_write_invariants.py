#!/usr/bin/env python3
"""PRE_QA_ULTRA_121 — validate_pre_qa_ultra_121_no_write_invariants.

Verifica statica read-only che gli invariant no-write sono mantenuti:

  * pre-battle-lobby.tsx contiene: is_preview, reward_policy,
    progress_policy, battle_engine_mode.
  * combat.tsx contiene: PREVIEW_REWARD_LOCK_ACTIVE,
    PREVIEW_NON_AUTHORITATIVE.
  * story.tsx / tower-of-the-hells.tsx / hero-training.tsx NON contengono
    chiamate HTTP mutanti (POST/PUT/PATCH/DELETE) verso endpoint
    reward/claim/grant/commit non-gated.
  * Nessun file 'gacha.tsx', 'shop.tsx', 'item-shop.tsx', 'vip.tsx',
    'battlepass.tsx' viene importato dal menu pubblico (verifica indiretta
    via menu.tsx / preQaNavGuard.ts: route bloccate).
  * Nessuna env flag live attiva (cerca pattern di flag = true noti tipo
    EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE, etc).

Read-only, no network, no DB.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
REPORTS_DIR = os.path.join(R, 'backend', 'reports', 'vertical_slice_qa')
os.makedirs(REPORTS_DIR, exist_ok=True)

PB_LOBBY = os.path.join(R, 'frontend', 'app', 'pre-battle-lobby.tsx')
COMBAT = os.path.join(R, 'frontend', 'app', 'combat.tsx')
STORY = os.path.join(R, 'frontend', 'app', 'story.tsx')
TOWER = os.path.join(R, 'frontend', 'app', 'tower-of-the-hells.tsx')
TRAINING = os.path.join(R, 'frontend', 'app', 'hero-training.tsx')
MENU = os.path.join(R, 'frontend', 'app', '(tabs)', 'menu.tsx')
GUARD = os.path.join(R, 'frontend', 'src', 'utils', 'preQaNavGuard.ts')

PB_REQUIRED = ['is_preview', 'reward_policy', 'progress_policy', 'battle_engine_mode']
COMBAT_REQUIRED = ['PREVIEW_REWARD_LOCK_ACTIVE', 'PREVIEW_NON_AUTHORITATIVE']

# Pattern HTTP mutanti.
_MUT_HTTP_RE = re.compile(
    r"(?:axios|apiClient|api|http|client)\s*\.\s*(?:post|put|patch|delete)\s*\(",
    re.IGNORECASE,
)
_FETCH_METHOD_RE = re.compile(r"method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)['\"]")

# Endpoint sensibili (sostituzione di mutation a reward/claim/grant/commit).
_SENSITIVE_ENDPOINT_RE = re.compile(
    r"/api/(?:reward|claim|grant|commit|achievement[s]?/claim|story/reward|"
    r"daily/claim|mail/claim|gacha|shop|vip|battlepass|iap)",
    re.IGNORECASE,
)

_BLOCK_COMMENT_RE = re.compile(r'/\*[\s\S]*?\*/')
_LINE_COMMENT_RE = re.compile(r'//[^\n]*')


def _strip_js_comments(src: str) -> str:
    s = _BLOCK_COMMENT_RE.sub('', src)
    s = _LINE_COMMENT_RE.sub('', s)
    return s


def _scan(fp: str) -> dict:
    if not os.path.exists(fp):
        return {'exists': False}
    src = open(fp, encoding='utf-8', errors='replace').read()
    code = _strip_js_comments(src)
    mut_calls = len(_MUT_HTTP_RE.findall(code)) + len(_FETCH_METHOD_RE.findall(code))
    sensitive = sorted(set(m.group(0).lower() for m in _SENSITIVE_ENDPOINT_RE.finditer(code)))
    return {
        'exists': True,
        'mut_http_count_in_code': mut_calls,
        'sensitive_endpoints_in_code': sensitive,
        'raw_len': len(src),
    }


def _has_tokens(fp: str, tokens: list) -> dict:
    if not os.path.exists(fp):
        return {'exists': False, 'missing': tokens, 'found': []}
    src = open(fp, encoding='utf-8', errors='replace').read()
    missing = [t for t in tokens if t not in src]
    found = [t for t in tokens if t in src]
    return {'exists': True, 'missing': missing, 'found': found}


def main() -> int:
    failures = []

    pb = _has_tokens(PB_LOBBY, PB_REQUIRED)
    if not pb['exists']:
        failures.append('pre-battle-lobby.tsx mancante')
    elif pb['missing']:
        failures.append(f'pre-battle-lobby.tsx missing tokens: {pb["missing"]}')

    cb = _has_tokens(COMBAT, COMBAT_REQUIRED)
    if not cb['exists']:
        failures.append('combat.tsx mancante')
    elif cb['missing']:
        failures.append(f'combat.tsx missing tokens: {cb["missing"]}')

    scans = {}
    for label, fp in (('story', STORY), ('tower', TOWER), ('training', TRAINING)):
        scans[label] = _scan(fp)
        if not scans[label]['exists']:
            failures.append(f'{label}.tsx mancante: {fp}')
            continue
        # Endpoint sensibili NON devono apparire nel codice eseguibile (commenti stripped).
        if scans[label]['sensitive_endpoints_in_code']:
            failures.append(
                f'{label}.tsx contiene endpoint sensibili nel codice: '
                f'{scans[label]["sensitive_endpoints_in_code"]}')

    # Verifica indiretta: menu.tsx + guard NON espongono shop/gacha/vip/bp/iap.
    if not os.path.exists(MENU) or not os.path.exists(GUARD):
        failures.append('menu.tsx o preQaNavGuard.ts mancante')
    else:
        guard_src = open(GUARD, encoding='utf-8').read()
        for r in ('/shop', '/vip', '/battlepass', '/gacha'):
            if f"'{r}'" not in guard_src:
                failures.append(f'preQaNavGuard.ts non blocca {r}')

    # Env flag: non cambiata. Verifichiamo solo che il file menu.tsx non
    # contenga un set di flag dev true hardcoded.
    if os.path.exists(MENU):
        menu_src = open(MENU, encoding='utf-8').read()
        if 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE = true' in menu_src or \
           "EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE='1'" in menu_src:
            failures.append('menu.tsx ha EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE attivato hardcoded')

    report = {
        'tool': 'validate_pre_qa_ultra_121_no_write_invariants',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'pre_battle_lobby_check': pb,
        'combat_check': cb,
        'scans': scans,
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(REPORTS_DIR, 'ultra_121_no_write_invariants_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[v121_no_write_invariants] {report['verdict']}")
    if failures:
        for f in failures:
            print(f'  - {f}')
        return 1
    print('  pb_tokens_ok=true combat_tokens_ok=true story/tower/training_no_sensitive_endpoints=true')
    return 0


if __name__ == '__main__':
    sys.exit(main())
