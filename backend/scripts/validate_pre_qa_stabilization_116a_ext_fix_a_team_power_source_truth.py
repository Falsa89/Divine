#!/usr/bin/env python3
"""Pre-QA Stabilization 116A-EXT FIX-A — Team Power Source Truth validator.

Validator statico + (opzionale) runtime evidence.

Check eseguiti:
  1. `backend/routes/battle_power.py` espone i nuovi campi metadata di
     truth (team_source, team_slot_count, valid_team_slot_count,
     invalid_team_slot_count, team_missing_reason).
  2. Logica di validita' slot: il route conta solo slot risolti verso
     (user_hero server-scoped posseduto E hero catalog visibile).
     Verifica statica: presenza variabili `valid_team_slot_count`/
     `invalid_team_slot_count` + accumulazione condizionale
     (`if is_valid:` ... `active_team_power += p`).
  3. Truth no-fake-team: se team_formation esiste ma valid=0
     → `team_missing=True` + `active_team_power=0`.
     Verifica statica via match della costante
     `TEAM_FORMATION_PRESENT_BUT_NO_VALID_SLOTS`.
  4. Owned heroes NON vengono sommati quando team manca: il path
     `team_missing=True` ritorna sempre `active_team_power=0`.
     Statico: dopo `if valid_team_slot_count == 0:` deve esserci
     `active_team_power = 0`.
  5. Nessun fallback `/api/team` account-wide nel route battle_power.py
     (non importa users, non legge legacy `users.team_formation`).
  6. NESSUN DB write nel route battle_power.py (no `$set/$inc/insert_one
     /update_one/delete_one` calls).
  7. Formula version invariata: `battle_power_v1_preqa_derived` (compat
     con validator 116A).
  8. Frontend `battle.tsx` NON reintroduce fallback `/api/team`
     account-wide. Il mapping della formation usa `slot_index` come
     fallback a `x/y` (truth: i team starter Pack 87 hanno solo
     slot_index, non x/y; il fix-A garantisce che vengano visualizzati).
  9. `frontend/app/(tabs)/home.tsx` continua a usare
     `useBattlePowerSummary` (no regressione).
 10. Out-of-scope: nessun touch a `battle_engine`, combat/tower
     runtime, gacha, red dot runtime, chat bot runtime.
 11. Pre-QA safety suite include il validator 116A-EXT FIX-A.
 12. (live) `GET /api/battle-power/summary?server_id=s1` con user
     autenticato espone i nuovi metadata. Skip SKIPPED_BACKEND_DOWN se
     backend down.
"""
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

ROUTE_FP = os.path.join(R, 'backend', 'routes', 'battle_power.py')
UTIL_FP = os.path.join(R, 'backend', 'utils', 'battle_power.py')
BATTLE_TSX_FP = os.path.join(R, 'frontend', 'app', '(tabs)', 'battle.tsx')
HOME_TSX_FP = os.path.join(R, 'frontend', 'app', '(tabs)', 'home.tsx')
SUITE_FP = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

BACKEND_PROBE_URL = 'http://127.0.0.1:8001/api/health'


def _read(fp: str) -> str:
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def check_route_exposes_truth_metadata():
    c = _read(ROUTE_FP)
    must = (
        '"team_source"',
        '"team_slot_count"',
        '"valid_team_slot_count"',
        '"invalid_team_slot_count"',
        '"team_missing_reason"',
    )
    missing = [k for k in must if k not in c]
    assert not missing, f'route non espone metadata truth: {missing}'
    print('[1] route exposes truth metadata (team_source/slot_count/valid/invalid/missing_reason) OK')


def check_slot_validity_counting():
    c = _read(ROUTE_FP)
    # Deve incrementare valid_team_slot_count solo se is_valid true.
    assert re.search(r'valid_team_slot_count\s*\+=\s*1', c), (
        'route non incrementa valid_team_slot_count'
    )
    assert re.search(r'invalid_team_slot_count\s*\+=\s*1', c), (
        'route non incrementa invalid_team_slot_count'
    )
    # Deve esserci accumulo condizionale di active_team_power solo su validity.
    # Strict: cerca `if is_valid:` seguito (a qualche riga) da
    # `active_team_power += p`.
    pattern = re.compile(r'if\s+is_valid\s*:\s*\n\s*active_team_power\s*\+=\s*p', re.MULTILINE)
    assert pattern.search(c), (
        'active_team_power non e\' accumulato condizionalmente a is_valid'
    )
    print('[2] slot validity counting (valid/invalid + conditional active_team_power) OK')


def check_no_fake_team():
    c = _read(ROUTE_FP)
    # Deve esserci il pattern "valid=0 → team_missing=True, power=0".
    assert 'TEAM_FORMATION_PRESENT_BUT_NO_VALID_SLOTS' in c, (
        'route non gestisce caso team_formation present ma 0 valid'
    )
    assert re.search(r'if\s+valid_team_slot_count\s*==\s*0\s*:', c), (
        'route non ha branch `if valid_team_slot_count == 0:`'
    )
    print('[3] no fake team (valid=0 → team_missing=True, power=0) OK')


def check_owned_not_summed_when_team_missing():
    c = _read(ROUTE_FP)
    # Nel branch del `team_missing == True` (valid=0), `active_team_power = 0`
    # deve essere riassegnato.
    idx = c.find('if valid_team_slot_count == 0:')
    assert idx >= 0
    branch = c[idx:idx + 800]
    assert 'team_missing = True' in branch, (
        'branch `valid_team_slot_count == 0` non setta `team_missing = True`'
    )
    assert re.search(r'active_team_power\s*=\s*0', branch), (
        'branch `valid_team_slot_count == 0` non resetta `active_team_power = 0`'
    )
    # Inoltre: NON ci deve essere un fallback ad `owned_hero_count` come
    # sorgente di `active_team_power` da nessuna parte nel route.
    forbidden_fallback = re.search(
        r'active_team_power\s*=\s*owned_hero',
        c,
    )
    assert not forbidden_fallback, (
        'route somma owned heroes come active_team_power (vietato)'
    )
    print('[4] owned heroes NOT summed when team missing OK')


def check_no_account_wide_team_fallback():
    c = _read(ROUTE_FP)
    # Vietato: route battle_power.py non deve leggere `users.team_formation`
    # ne fare get-formation senza server_id.
    forbidden = (
        'users.team_formation',
        'db.users.find_one',  # se aprisse `users` legacy
        'legacy_account',
    )
    for tok in forbidden:
        assert tok not in c, f'route battle_power.py contiene token account-wide vietato: {tok}'
    print('[5] no account-wide team fallback in battle_power route OK')


def check_no_db_writes():
    c = _read(ROUTE_FP)
    forbidden_calls = (
        r'\.insert_one\s*\(', r'\.insert_many\s*\(',
        r'\.update_one\s*\(', r'\.update_many\s*\(',
        r'\.delete_one\s*\(', r'\.delete_many\s*\(',
        r'\.replace_one\s*\(', r'\.find_one_and_update\s*\(',
        r'\.find_one_and_delete\s*\(', r'\.bulk_write\s*\(',
    )
    forbidden_ops = (r'["\']\$set["\']', r'["\']\$inc["\']', r'["\']\$push["\']')
    for pat in forbidden_calls + forbidden_ops:
        m = re.search(pat, c)
        assert not m, f'battle_power.py contiene mutation pattern: {pat!r} → {m.group(0)!r}'
    print('[6] no DB writes in battle_power route OK')


def check_formula_version_invariant():
    c = _read(UTIL_FP)
    assert 'battle_power_v1_preqa_derived' in c, (
        'formula_version mutata (DEVE restare battle_power_v1_preqa_derived)'
    )
    print('[7] formula version invariata (battle_power_v1_preqa_derived) OK')


def check_battle_tsx_no_account_wide_and_uses_slot_index():
    c = _read(BATTLE_TSX_FP)
    # No fallback `/api/team` account-wide.
    forbidden_account_wide = re.findall(r"apiCall\(\s*['\"]\/api\/team['\"]\s*[\),]", c)
    assert not forbidden_account_wide, (
        f'battle.tsx reintroduce `/api/team` account-wide: {forbidden_account_wide}'
    )
    # Deve usare `/api/team/get-formation` con server_id.
    assert '/api/team/get-formation' in c, (
        'battle.tsx non usa /api/team/get-formation server-scoped'
    )
    # Fix-A: deve gestire `slot_index` come fallback a `x`/`y`.
    assert 'slot_index' in c, (
        'battle.tsx non gestisce f.slot_index (richiesto da Pack 87 starter team)'
    )
    print('[8] battle.tsx: no /api/team account-wide + supporta slot_index OK')


def check_home_uses_hook_still():
    c = _read(HOME_TSX_FP)
    assert 'useBattlePowerSummary' in c, (
        'home.tsx non usa piu\' useBattlePowerSummary (regressione)'
    )
    print('[9] home.tsx still uses useBattlePowerSummary (no regression) OK')


def check_no_out_of_scope():
    pack_files = (ROUTE_FP, UTIL_FP, BATTLE_TSX_FP, HOME_TSX_FP)
    forbidden_patterns = (
        r'^\s*from\s+\S*battle_engine\b',
        r'^\s*from\s+\S*combat_runtime\b',
        r'^\s*from\s+\S*tower_runtime\b',
        r'^\s*from\s+\S*gacha_rates_runtime\b',
        r'^\s*from\s+\S*red_dot_runtime\b',
        r'^\s*from\s+\S*chat_bot_runtime\b',
    )
    offenders = []
    for fp in pack_files:
        c = _read(fp)
        for pat in forbidden_patterns:
            if re.search(pat, c, flags=re.MULTILINE):
                offenders.append((os.path.basename(fp), pat))
    assert not offenders, f'out-of-scope imports: {offenders}'
    print('[10] no out-of-scope imports OK')


def check_suite_registration():
    c = _read(SUITE_FP)
    must = 'validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py'
    assert must in c, f'suite non registra validator FIX-A: {must!r}'
    print('[11] pre-QA safety suite registers 116A-EXT FIX-A OK')


def _backend_up() -> bool:
    try:
        with urllib.request.urlopen(BACKEND_PROBE_URL, timeout=2) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        return False


def check_runtime_summary_truth_metadata():
    if not _backend_up():
        print('[12] SKIPPED_BACKEND_DOWN — runtime summary truth metadata check skipped')
        return 'skipped'
    # Crea un user effimero + PSP + (no starter) per verificare che il
    # summary risponda con team_missing_reason=TEAM_FORMATION_EMPTY (PSP
    # senza team_formation).
    import urllib.request as _ur
    import urllib.parse as _up
    import uuid as _uuid
    # Register
    email = f"qa_fix_a_{_uuid.uuid4().hex[:8]}@test.com"
    password = "QaFixA_" + _uuid.uuid4().hex[:8]
    body = json.dumps({"email": email, "password": password, "username": f"qa{_uuid.uuid4().hex[:6]}"}).encode('utf-8')
    req = _ur.Request('http://127.0.0.1:8001/api/register', data=body, headers={"Content-Type": "application/json"}, method='POST')
    try:
        with _ur.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            token = d.get('access_token') or d.get('token')
    except (urllib.error.URLError, OSError) as e:
        print(f'[12] SKIPPED_BACKEND_DOWN — register failed: {e}')
        return 'skipped'
    assert token, 'register did not return token'
    # PSP ensure (no starter claim → team_formation will be empty)
    req = _ur.Request('http://127.0.0.1:8001/api/psp/ensure?server_id=s1', method='POST',
                      headers={"Authorization": f"Bearer {token}"})
    with _ur.urlopen(req, timeout=10) as resp:
        resp.read()
    # Now hit summary. Expect team_missing_reason=TEAM_FORMATION_EMPTY.
    req = _ur.Request('http://127.0.0.1:8001/api/battle-power/summary?server_id=s1',
                      headers={"Authorization": f"Bearer {token}"})
    with _ur.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read())
    assert d.get('status') == 'ok', f'unexpected status: {d.get("status")}'
    assert d.get('team_missing') is True, f'team_missing should be True for fresh PSP (got {d.get("team_missing")})'
    assert d.get('team_missing_reason') == 'TEAM_FORMATION_EMPTY', (
        f'team_missing_reason should be TEAM_FORMATION_EMPTY (got {d.get("team_missing_reason")!r})'
    )
    assert d.get('active_team_power') == 0, 'active_team_power should be 0'
    assert d.get('team_slot_count') == 0
    assert d.get('valid_team_slot_count') == 0
    assert d.get('invalid_team_slot_count') == 0
    print('[12] runtime summary truth metadata OK (PSP-only no team: team_missing=True, reason=TEAM_FORMATION_EMPTY)')
    return 'ok'


def main() -> int:
    check_route_exposes_truth_metadata()
    check_slot_validity_counting()
    check_no_fake_team()
    check_owned_not_summed_when_team_missing()
    check_no_account_wide_team_fallback()
    check_no_db_writes()
    check_formula_version_invariant()
    check_battle_tsx_no_account_wide_and_uses_slot_index()
    check_home_uses_hook_still()
    check_no_out_of_scope()
    check_suite_registration()
    rt = check_runtime_summary_truth_metadata()
    suffix = ' (runtime SKIPPED_BACKEND_DOWN)' if rt == 'skipped' else ''
    print(
        '[v116A_EXT_FIX_A PRE_QA_116A_EXT_FIX_A_TEAM_POWER_SOURCE_TRUTH] OK '
        'route_truth_metadata slot_validity_counting no_fake_team '
        'owned_not_summed no_account_wide no_db_writes formula_invariant '
        'battle_tsx_slot_index home_hook_no_regression no_out_of_scope '
        'suite_registered runtime_summary_truth' + suffix
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
