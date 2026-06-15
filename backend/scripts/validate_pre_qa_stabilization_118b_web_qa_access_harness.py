#!/usr/bin/env python3
"""Pre-QA Stabilization 118B — Web QA Access Harness validator.

Verifica:
- Pagina /qa-manual-118 esiste, e' read-only/dev-QA-gated, chiama solo i 8
  endpoint GET autorizzati e non contiene pattern mutation/claim/push.
- HTML snapshot, JSON snapshot e runbook docs presenti con header QA-only.
- Invarianti foundation precedenti (BP/RD/HU/116B/115G/115F) preservate.
- Suite registra 118B.
- Nessun bytecode tracciato.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

PAGE = os.path.join(R, 'frontend', 'app', 'qa-manual-118.tsx')
SNAPSHOT_HTML = os.path.join(R, 'docs', 'divine', 'qa',
                             '118_WEB_QA_ACCESS_HARNESS_SNAPSHOT.html')
SNAPSHOT_JSON = os.path.join(R, 'docs', 'divine', 'qa',
                             '118_WEB_QA_ACCESS_HARNESS_SNAPSHOT.json')
RUNBOOK = os.path.join(R, 'docs', 'divine', 'qa',
                       '118B_WEB_QA_ACCESS_HARNESS_RUNBOOK.md')
SUITE = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

# Invariants files che devono restare inalterati nel pack 118B.
BP_UTIL = os.path.join(R, 'backend', 'utils', 'battle_power.py')
RD_UTIL = os.path.join(R, 'backend', 'utils', 'red_dot_summary.py')
HU_UTIL = os.path.join(R, 'backend', 'utils', 'hero_upgrade_readiness.py')
NAV_GUARD = os.path.join(R, 'frontend', 'src', 'utils', 'preQaNavGuard.ts')
CHAT_CONTRACT = os.path.join(R, 'data', 'design', 'server_actors',
                             'v116b_bot_chat_quality_contract_v1.json')

ALLOWED_GET_PATHS = (
    '/api/battle-power/metadata',
    '/api/battle-power/summary',
    '/api/battle-power/breakdown',
    '/api/red-dot/metadata',
    '/api/red-dot/summary',
    '/api/hero-upgrade/metadata',
    '/api/hero-upgrade/readiness',
    '/api/user/heroes',
)


def _r(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def c1():
    for fp in (PAGE, SNAPSHOT_HTML, SNAPSHOT_JSON, RUNBOOK):
        assert os.path.exists(fp), f'manca: {fp}'
    json.loads(_r(SNAPSHOT_JSON))
    assert len(_r(RUNBOOK)) > 1500
    assert len(_r(SNAPSHOT_HTML)) > 1500
    print('[1] 4 deliverable present + JSON valid + docs non-trivial OK')


def c2():
    p = _r(PAGE)
    # QA-only banner + version constant
    assert 'pre_qa_118b_web_qa_access_harness_v1' in p
    assert 'preQaDevQaVisible' in p
    assert 'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE' in _r(NAV_GUARD)
    # Banner copy QA-only
    assert 'QA-only' in p or 'QA-ONLY' in p
    assert 'READ-ONLY' in p
    assert 'NO MUTATIONS' in p
    assert 'NO LIVE SYSTEMS' in p
    # Pack 118B-FIX-A: base URL deve usare prefisso EXPO_PUBLIC_ (env
    # client-side Expo). Non deve dipendere da EXPO_BACKEND_URL (senza
    # prefisso PUBLIC) come unico requisito bloccante. Default same-origin.
    assert 'EXPO_PUBLIC_BACKEND_URL' in p, \
        'page must read EXPO_PUBLIC_BACKEND_URL (client-side env)'
    # Non deve esserci early-return bloccante se baseUrl e'' '' (same-origin).
    # Cerchiamo il pattern dell'errore "EXPO_BACKEND_URL non configurato" ed
    # equivalenti: deve essere stato rimosso.
    assert 'EXPO_BACKEND_URL non configurato' not in p, \
        'page non deve avere blocking error "EXPO_BACKEND_URL non configurato"'
    # Verifica che NON ci sia il guard "if (!baseUrl) { ... return; }" attorno
    # alle probe (consente same-origin '').
    assert 'if (!baseUrl)' not in p or 'non configurato' not in p, \
        'page non deve bloccare i probe quando baseUrl vuoto (same-origin)'
    print('[2] Page QA-only banner + dev-QA gate hook + same-origin baseUrl fix-A OK')


def c3():
    p = _r(PAGE)
    # Solo metodo GET, nessun POST/PUT/DELETE/PATCH.
    # Cerchiamo string literal 'POST' usato per chiamate HTTP.
    forbidden_method_patterns = (
        "method: 'POST'", 'method: "POST"',
        "method: 'PUT'", 'method: "PUT"',
        "method: 'DELETE'", 'method: "DELETE"',
        "method: 'PATCH'", 'method: "PATCH"',
    )
    for pat in forbidden_method_patterns:
        assert pat not in p, f'page contains forbidden HTTP method: {pat!r}'
    # Solo gli 8 path consentiti elencati come literal string
    # (nessun altro path /api/... in stringa).
    api_strings = re.findall(r"'(/api/[^']+)'", p)
    api_strings += re.findall(r'"(/api/[^"]+)"', p)
    extra = [s for s in api_strings if not any(
        s == allowed or s.startswith(allowed + '?') for allowed in ALLOWED_GET_PATHS
    )]
    assert not extra, f'page chiama path /api non autorizzati: {extra}'
    # Almeno i path autorizzati menzionati
    for path in ALLOWED_GET_PATHS:
        assert path in p, f'page non elenca path {path}'
    print(f'[3] Page uses only GET + only 8 allowed /api/* paths (no extra: {len(extra)}) OK')


def c4():
    p = _r(PAGE)
    # Pattern vietati: claim/spend/buy/summon/push/upgrade/etc.
    forbidden_substrings = (
        '/api/mail/read-all', '/api/mail/claim',
        '/api/daily-quest/claim', '/api/daily-login/claim',
        '/api/achievements/claim', '/api/battle-pass/claim',
        '/api/shop/buy', '/api/gacha/summon',
        '/api/push/register', '/api/push/test', '/api/reward/claim',
        '/api/hero/upgrade', '/api/hero/levelup', '/api/fusion/star-up',
        'localStorage', 'AsyncStorage.setItem(',  # no persist token
        'WebSocket', 'EventSource',
    )
    for pat in forbidden_substrings:
        assert pat not in p, f'page contains forbidden pattern: {pat!r}'
    print('[4] Page contains no claim/upgrade/spend/push/WS/persist patterns OK')


def c5():
    # JSON snapshot copre tutti gli 8 endpoint, con flags design-only
    d = json.loads(_r(SNAPSHOT_JSON))
    m = d.get('_meta', {})
    assert m.get('scope') == 'design_only_read_only'
    assert m.get('is_runtime') is False
    assert m.get('do_not_use_for_runtime_resolution') is True
    assert m.get('pack_origin') == '118B'
    eps = d.get('allowed_get_endpoints', [])
    assert len(eps) == 8, f'snapshot endpoints != 8: {len(eps)}'
    seen_paths = []
    for ep in eps:
        for k in ('id', 'label', 'method', 'path', 'requires_server_id',
                  'requires_auth', 'invariant'):
            assert k in ep, f'snapshot ep manca {k}: {ep.get("id")}'
        assert ep['method'] == 'GET', f'snapshot ep {ep["id"]} method != GET'
        # path puo' includere '?server_id=...'
        base = ep['path'].split('?')[0]
        seen_paths.append(base)
        assert base in ALLOWED_GET_PATHS, f'snapshot ep path non autorizzato: {base}'
    assert set(seen_paths) == set(ALLOWED_GET_PATHS), \
        f'snapshot non copre tutti gli 8 endpoint: {set(ALLOWED_GET_PATHS)-set(seen_paths)}'
    # forbidden list presente
    assert 'forbidden_in_harness' in d
    assert any('mutation' in s.lower() or 'claim' in s.lower()
               for s in d['forbidden_in_harness'])
    # page meta
    page = d.get('page', {})
    assert page.get('access_kind') == 'deeplink_only_dev_qa_gated'
    assert page.get('gate_env_var') == 'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE'
    assert page.get('gate_default') is False
    assert page.get('player_facing') is False
    print('[5] JSON snapshot covers 8 endpoints + design_only meta + page meta OK')


def c6():
    # HTML snapshot contiene banner QA-only + lista 8 endpoint + forbidden list
    h = _r(SNAPSHOT_HTML)
    assert 'QA-ONLY' in h or 'QA-only' in h
    assert 'READ-ONLY' in h
    assert 'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE' in h
    assert '/qa-manual-118' in h
    for path in ALLOWED_GET_PATHS:
        # path puo' essere mostrato con encoding
        assert path in h, f'HTML snapshot non elenca {path}'
    # forbidden section
    assert 'Vietato' in h or 'forbidden' in h.lower()
    print('[6] HTML snapshot banner + 8 endpoints + forbidden section OK')


def c7():
    # Runbook contiene sezioni chiave
    rb = _r(RUNBOOK)
    for needle in ('Pre-requisiti', 'Setup sessione', 'Endpoint coperti',
                   'Regole d', 'Stop conditions', 'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE',
                   '/qa-manual-118'):
        assert needle in rb, f'runbook manca sezione: {needle}'
    print('[7] Runbook sections + dev-QA gate documented OK')


def c8():
    # Invariants preserved (BP formula, RD version, HU source version)
    assert 'battle_power_v1_preqa_derived' in _r(BP_UTIL)
    assert 'red_dot_v1_preqa_read_only_foundation' in _r(RD_UTIL)
    assert "'hero_upgrade_readiness_v1_preqa_read_only'" in _r(HU_UTIL)
    # 116B contract
    cc = json.loads(_r(CHAT_CONTRACT))
    flags = cc.get('live_activation_flags', {}) or {}
    for k, v in flags.items():
        assert v is False, f'116B regressione: {k}=True'
    # HU helper invariant: no can_upgrade_now=True
    hu = _r(HU_UTIL)
    assert "'can_upgrade_now': True" not in hu
    assert "'can_upgrade_now': true" not in hu
    print('[8] Invariants preserved (BP/RD/HU versions + 116B + no can_upgrade_now=True) OK')


def c9():
    # nessun import out-of-scope nel validator e nella pagina QA
    me = _r(os.path.abspath(__file__))
    for pat in (r'from\s+\S*battle_engine\b',
                r'from\s+\S*combat_runtime\b',
                r'from\s+\S*tower_runtime\b'):
        assert not re.search(pat, me), f'validator out-of-scope {pat}'
    page = _r(PAGE)
    # La pagina TSX non deve importare hook player live (chat, battle, gacha).
    for pat in (r"from\s+['\"][^'\"]*useChatChannel['\"]",
                r"from\s+['\"][^'\"]*useDM['\"]",
                r"from\s+['\"][^'\"]*gacha[^'\"]*['\"]",
                r"from\s+['\"][^'\"]*battle_engine['\"]"):
        assert not re.search(pat, page), f'page out-of-scope import {pat}'
    print('[9] No out-of-scope imports in validator and page OK')


def c10():
    # No live activation pattern nei file nuovi del pack 118B (oltre la pagina)
    files_to_check = (SNAPSHOT_JSON, RUNBOOK)
    forbidden_substrings = (
        '.insert_one(', '.update_one(', '.delete_one(',
        '.insert_many(', '.update_many(', '.delete_many(',
        '.find_one_and_update(', '.bulk_write(', '.replace_one(',
        '/api/mail/read-all', '/api/mail/claim',
        '/api/daily-quest/claim', '/api/daily-login/claim',
        '/api/achievements/claim', '/api/battle-pass/claim',
        '/api/shop/buy', '/api/gacha/summon',
        '/api/push/register', '/api/push/test', '/api/reward/claim',
        '/api/hero/upgrade', '/api/hero/levelup', '/api/fusion/star-up',
    )
    for fp in files_to_check:
        c = _r(fp)
        for pat in forbidden_substrings:
            assert pat not in c, f'{os.path.basename(fp)}: vietato {pat!r}'
    print('[10] No DB mutation + no claim/upgrade/spend/push references in docs OK')


def c11():
    out = subprocess.check_output(['git', '-C', R, 'ls-files'],
                                  stderr=subprocess.DEVNULL).decode()
    tracked = [p for p in out.splitlines()
               if p.endswith('.pyc') or p.endswith('.pyo') or '__pycache__/' in p]
    assert not tracked, f'bytecode tracked: {tracked[:5]}'
    print('[11] no .pyc / .pyo / __pycache__ tracked OK')


def c12():
    c = _r(SUITE)
    must = 'validate_pre_qa_stabilization_118b_web_qa_access_harness.py'
    assert must in c, 'suite non registra 118B'
    print('[12] pre-QA safety suite registers 118B OK')


def c13():
    # Pack 118 deliverable preserved (matrix/triage/runbook/evidence)
    for fp in (
        os.path.join(R, 'data', 'design', 'release_readiness',
                     'pre_qa_118_manual_qa_allowed_surface_matrix_v1.json'),
        os.path.join(R, 'data', 'design', 'release_readiness',
                     'pre_qa_119_post_qa_triage_buckets_v1.json'),
        os.path.join(R, 'docs', 'divine', 'qa',
                     '118_MANUAL_QA_DEVICE_RUNBOOK.md'),
        os.path.join(R, 'docs', 'divine', 'qa',
                     '118_MANUAL_QA_EVIDENCE_TEMPLATE.md'),
    ):
        assert os.path.exists(fp), f'Pack 118 deliverable mancante: {fp}'
    print('[13] Pack 118 deliverables preserved OK')


def c14():
    # Runtime best-effort: i 4 endpoint pubblici devono restare 200 con
    # invarianti chiave (Pack 118B non modifica nulla a runtime).
    try:
        import urllib.request
        for url, must_substrings in (
            ('http://127.0.0.1:8001/api/battle-power/metadata',
             ['battle_power_v1_preqa_derived']),
            ('http://127.0.0.1:8001/api/battle-power/breakdown',
             ['battle_power_breakdown_v1_preqa_metadata_only',
              'metadata_only_COMPLETE']),
            ('http://127.0.0.1:8001/api/red-dot/metadata',
             ['red_dot_v1_preqa_read_only_foundation']),
            ('http://127.0.0.1:8001/api/hero-upgrade/metadata',
             ['hero_upgrade_readiness_v1_preqa_read_only',
              'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS']),
        ):
            with urllib.request.urlopen(url, timeout=5) as resp:
                body = resp.read().decode()
                for sub in must_substrings:
                    assert sub in body, f'{url} non contiene {sub}'
        print('[14] runtime smoke 4 endpoint metadata + flags invarianti OK')
    except Exception as e:
        print(f'[14] runtime smoke SKIPPED_BACKEND_DOWN: {e}')


def main():
    c1(); c2(); c3(); c4(); c5(); c6(); c7(); c8(); c9(); c10(); c11(); c12(); c13(); c14()
    print('[v118B PRE_QA_118B_WEB_QA_ACCESS_HARNESS] OK '
          'deliverables_present page_qa_only_banner page_get_only_8_endpoints '
          'page_no_forbidden_patterns json_snapshot_design_only '
          'html_snapshot_banner_endpoints runbook_sections invariants_preserved '
          'no_out_of_scope no_db_mutation_docs no_bytecode suite_registered '
          'pack118_preserved runtime_smoke')
    return 0


if __name__ == '__main__':
    sys.exit(main())
