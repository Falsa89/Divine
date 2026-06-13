#!/usr/bin/env python3
"""Pre-QA Stabilization 116A — Battle Power Foundation validator.

Validator statico + (opzionale) curl evidence se backend up.

Check (almeno):
  1. Backend utility `backend/utils/battle_power.py` esiste e dichiara
     `BATTLE_POWER_FORMULA_VERSION = "battle_power_v1_preqa_derived"`.
  2. Backend route `backend/routes/battle_power.py` esiste, dichiara
     `GET /battle-power/summary`, richiede `server_id` (no silent s1).
  3. Route/utility sono read-only: nessun `$set`/`$inc`/`insert_one`/
     `update_one`/`delete_one`/`update_many`/`delete_many`/`insert_many`
     nel modulo route e nel modulo utility.
  4. Output dichiara `runtime_attached=false`, `combat_authoritative=false`,
     `reward_authoritative=false`, `balance_final=false` (verificato sui
     metadata builder).
  5. La formula esclude esplicitamente artifacts/divine weapons/cosmetics/
     titles/skill final_numbers/live rewards (dichiarato in
     `BATTLE_POWER_EXCLUDED_SOURCES`).
  6. Home (`frontend/app/(tabs)/home.tsx`) NON usa piu'
     `user?.power || user?.total_power || 0` come sorgente finale di display
     (verifica statica: la stringa esatta non e' piu' presente).
  7. Home usa il nuovo hook `useBattlePowerSummary` e mostra `powerLabel`
     (placeholder onesto), non `Number(power).toLocaleString()` come sorgente
     finale del display power.
  8. Battle tab (`frontend/app/(tabs)/battle.tsx`) NON reintroduce il
     fallback `/api/team` account-wide (continua a usare
     `/api/team/get-formation?server_id=...`) e usa l'hook
     `useBattlePowerSummary` per il display power.
  9. Out-of-scope: nessuna modifica/riferimento a `battle_engine`,
     combat runtime, gacha_rates, character_bible, skill_catalog,
     `data/design/**` nei file scope-autorizzati di 116A.
 10. Pre-QA safety suite (`run_pre_qa_safety_validator_suite.py`) include
     il validator 116A.

Esecuzione live (se backend up):
 11. `GET /api/battle-power/metadata` → 200 con `formula_version` corretta.
 12. (Opzionale auth) — se possibile creare utente effimero, verificare
     `summary` senza server_id → 400 SERVER_ID_REQUIRED, con server_id=s1
     → 200 envelope blocked_no_psp_for_server o ok.

Skip: se backend down, marcare il check 11 come `SKIPPED_BACKEND_DOWN`
(NOT pass) ma il validator non fallisce per quel solo motivo.
"""
import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

UTIL_FP = os.path.join(R, 'backend', 'utils', 'battle_power.py')
ROUTE_FP = os.path.join(R, 'backend', 'routes', 'battle_power.py')
HOME_FP = os.path.join(R, 'frontend', 'app', '(tabs)', 'home.tsx')
BATTLE_FP = os.path.join(R, 'frontend', 'app', '(tabs)', 'battle.tsx')
HERO_DETAIL_FP = os.path.join(R, 'frontend', 'app', 'hero-detail.tsx')
SUITE_FP = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

BACKEND_PROBE_URL = os.environ.get(
    'PRE_QA_116A_BACKEND_PROBE_URL', 'http://127.0.0.1:8001/api/health'
)
METADATA_URL = 'http://127.0.0.1:8001/api/battle-power/metadata'


def _read(fp: str) -> str:
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


# ---- [1] util module exists + formula version ------------------------------
def check_util_module():
    assert os.path.exists(UTIL_FP), f'manca {UTIL_FP}'
    c = _read(UTIL_FP)
    assert 'BATTLE_POWER_FORMULA_VERSION' in c, 'manca BATTLE_POWER_FORMULA_VERSION'
    assert '"battle_power_v1_preqa_derived"' in c or "'battle_power_v1_preqa_derived'" in c, (
        'BATTLE_POWER_FORMULA_VERSION non e\' battle_power_v1_preqa_derived'
    )
    # Metadata flags
    must = (
        'BATTLE_POWER_RUNTIME_ATTACHED = False',
        'BATTLE_POWER_COMBAT_AUTHORITATIVE = False',
        'BATTLE_POWER_REWARD_AUTHORITATIVE = False',
        'BATTLE_POWER_BALANCE_FINAL = False',
    )
    missing = [m for m in must if m not in c]
    assert not missing, f'utility: metadata flag mancanti: {missing}'
    print('[1] util battle_power module + formula version OK')


# ---- [2] route module exists + endpoint shape ------------------------------
def check_route_module():
    assert os.path.exists(ROUTE_FP), f'manca {ROUTE_FP}'
    c = _read(ROUTE_FP)
    assert 'APIRouter' in c, 'route non usa APIRouter'
    assert 'prefix="/api/battle-power"' in c, 'route non e\' prefisso /api/battle-power'
    assert '@router.get("/summary")' in c, 'manca GET /summary'
    # server_id required (no silent s1 fallback): la route deve sollevare
    # HTTPException(400, "SERVER_ID_REQUIRED") se sid e' empty/None.
    assert 'SERVER_ID_REQUIRED' in c, 'route non solleva SERVER_ID_REQUIRED'
    # No silent s1 fallback: deve dichiararlo (commento o constant) e non
    # avere `server_id or "s1"` o `sid = sid or "s1"`.
    forbidden_fallbacks = (
        'server_id or "s1"',
        "server_id or 's1'",
        'sid or "s1"',
        "sid or 's1'",
        'server_id="s1"',
        'default="s1"',
    )
    for pat in forbidden_fallbacks:
        assert pat not in c, f'route contiene silent s1 fallback: {pat!r}'
    print('[2] route module + endpoint shape (no silent s1 fallback) OK')


# ---- [3] read-only: no mutation calls -------------------------------------
def check_read_only():
    # Pattern strict: cerca CHIAMATE reali (es. `.insert_one(`, `.update_one(`),
    # non menzioni in docstring/commento. Per i mongo operator usiamo
    # `'$set'` / `"$set"` (in quotes) come pattern di operator query.
    forbidden_call_patterns = (
        r'\.insert_one\s*\(',
        r'\.insert_many\s*\(',
        r'\.update_one\s*\(',
        r'\.update_many\s*\(',
        r'\.delete_one\s*\(',
        r'\.delete_many\s*\(',
        r'\.replace_one\s*\(',
        r'\.find_one_and_update\s*\(',
        r'\.find_one_and_delete\s*\(',
        r'\.find_one_and_replace\s*\(',
        r'\.bulk_write\s*\(',
    )
    forbidden_operator_patterns = (
        r'["\']\$set["\']',
        r'["\']\$inc["\']',
        r'["\']\$push["\']',
        r'["\']\$addToSet["\']',
        r'["\']\$pull["\']',
        r'["\']\$unset["\']',
    )
    for fp in (UTIL_FP, ROUTE_FP):
        c = _read(fp)
        for pat in forbidden_call_patterns + forbidden_operator_patterns:
            m = re.search(pat, c)
            assert not m, (
                f'{os.path.basename(fp)}: contiene mutation pattern vietato: {pat!r} '
                f'→ match={m.group(0)!r}'
            )
    print('[3] util + route are READ-ONLY (no insert/update/delete calls, no $set/$inc operators) OK')


# ---- [4] output declares non-authoritative flags --------------------------
def check_output_flags():
    c_util = _read(UTIL_FP)
    # build_battle_power_metadata deve esistere e ritornare i flag corretti.
    assert 'def build_battle_power_metadata' in c_util, (
        'utility: manca build_battle_power_metadata'
    )
    must_keys = (
        '"formula_version"', '"source"',
        '"runtime_attached"', '"combat_authoritative"',
        '"reward_authoritative"', '"balance_final"',
        '"excluded_power_sources"',
    )
    missing = [k for k in must_keys if k not in c_util]
    assert not missing, f'metadata builder mancano chiavi: {missing}'
    print('[4] metadata builder declares non-authoritative flags OK')


# ---- [5] excluded sources dichiarati ---------------------------------------
def check_excluded_sources():
    c_util = _read(UTIL_FP)
    must_excluded = (
        '"artifacts"', '"divine_weapons"', '"cosmetics"', '"titles"',
        '"skill_final_numbers"', '"live_rewards"',
    )
    missing = [k for k in must_excluded if k not in c_util]
    assert not missing, f'EXCLUDED_SOURCES non dichiara: {missing}'
    print('[5] excluded sources (artifacts/divine_weapons/cosmetics/titles/skill_final_numbers/live_rewards) dichiarati OK')


# ---- [6] Home no longer uses user?.power || user?.total_power || 0 --------
def check_home_no_legacy_power_source():
    c = _read(HOME_FP)
    legacy_pat = 'user?.power || user?.total_power || 0'
    assert legacy_pat not in c, (
        f'Home usa ancora la sorgente legacy stale: {legacy_pat!r}'
    )
    print('[6] Home no longer uses `user?.power || user?.total_power || 0` OK')


# ---- [7] Home uses useBattlePowerSummary hook -----------------------------
def check_home_uses_battle_power_hook():
    c = _read(HOME_FP)
    assert 'useBattlePowerSummary' in c, (
        'Home non importa il nuovo hook useBattlePowerSummary'
    )
    # Deve usare la label hook-derived almeno in una <Text> per il valore.
    assert 'powerLabel' in c or 'displayTeamPowerLabel' in c, (
        'Home non usa la label hook-derived (powerLabel/displayTeamPowerLabel)'
    )
    # Non deve usare piu' `Number(power).toLocaleString()` come display power.
    assert 'Number(power).toLocaleString()' not in c, (
        'Home usa ancora `Number(power).toLocaleString()` come display power'
    )
    print('[7] Home uses useBattlePowerSummary hook + honest placeholders OK')


# ---- [8] Battle tab no /api/team account-wide + uses hook ------------------
def check_battle_tab_no_account_wide_team():
    c = _read(BATTLE_FP)
    # Pattern vietato: `apiCall('/api/team')` o `apiCall("/api/team")` (path
    # ESATTO senza `/get-formation`). Lo strict server-scoped path autorizzato
    # e' `/api/team/get-formation?server_id=...`.
    forbidden = re.findall(r"apiCall\(\s*['\"]\/api\/team['\"]\s*[\),]", c)
    assert not forbidden, (
        f'Battle tab reintroduce fallback `/api/team` account-wide: {forbidden}'
    )
    assert 'useBattlePowerSummary' in c, (
        'Battle tab non usa useBattlePowerSummary (richiesto per display server-scoped)'
    )
    # Non deve usare piu' `power.toLocaleString()` come display power.
    assert 'power.toLocaleString()' not in c, (
        'Battle tab usa ancora `power.toLocaleString()` come display power'
    )
    # Deve continuare a usare l'endpoint strict server-scoped per la formation.
    assert '/api/team/get-formation' in c, (
        'Battle tab non usa piu\' /api/team/get-formation server-scoped'
    )
    print('[8] Battle tab no /api/team account-wide + uses hook + server-scoped formation OK')


# ---- [9] no out-of-scope changes ------------------------------------------
def check_no_out_of_scope():
    pack_files = (UTIL_FP, ROUTE_FP, HOME_FP, BATTLE_FP, HERO_DETAIL_FP)
    forbidden_patterns = (
        r'^\s*from\s+\S*battle_engine\b',
        r'^\s*import\s+\S*battle_engine\b',
        r'^\s*from\s+\S*combat_runtime\b',
        r'^\s*from\s+\S*gacha_rates\b',
        r'^\s*from\s+\S*character_bible\b',
        r'^\s*from\s+\S*skill_catalog_runtime\b',
        # frontend equivalents
        r"from\s+['\"][^'\"]*battle_engine[^'\"]*['\"]",
        r"from\s+['\"][^'\"]*combat_runtime[^'\"]*['\"]",
    )
    offenders = []
    for fp in pack_files:
        if not os.path.exists(fp):
            continue
        c = _read(fp)
        for pat in forbidden_patterns:
            if re.search(pat, c, flags=re.MULTILINE):
                offenders.append((os.path.basename(fp), pat))
    assert not offenders, f'out-of-scope import detected: {offenders}'
    # Inoltre i file backend del pack non devono scrivere sotto data/design/.
    write_pat = re.compile(
        r"open\(\s*[^,\)]*data/design[^,\)]*,\s*['\"]w[+ab]?['\"]"
    )
    for fp in (UTIL_FP, ROUTE_FP):
        c = _read(fp)
        assert not write_pat.search(c), f'{fp}: scrive sotto data/design/ (vietato)'
    print('[9] no out-of-scope imports + no data/design writes OK')


# ---- [10] pre-QA safety suite includes 116A -------------------------------
def check_pre_qa_safety_suite_registration():
    c = _read(SUITE_FP)
    must = 'validate_pre_qa_stabilization_116a_battle_power_foundation.py'
    assert must in c, f'pre-QA safety suite non registra 116A: manca {must!r}'
    print('[10] pre-QA safety suite includes 116A validator OK')


# ---- [11] runtime live: metadata endpoint reachable -----------------------
def _backend_up() -> bool:
    try:
        with urllib.request.urlopen(BACKEND_PROBE_URL, timeout=2) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        return False


def check_runtime_metadata_endpoint():
    if not _backend_up():
        # Truthful: skip esplicito, NON pass.
        print('[11] SKIPPED_BACKEND_DOWN — runtime metadata endpoint check skipped')
        return 'skipped'
    try:
        with urllib.request.urlopen(METADATA_URL, timeout=3) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            status = resp.status
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
        # Honest fail.
        raise AssertionError(f'runtime metadata endpoint unreachable: {e}')
    assert status == 200, f'metadata HTTP={status}'
    d = json.loads(body)
    assert d.get('formula_version') == 'battle_power_v1_preqa_derived', (
        f'formula_version inattesa: {d.get("formula_version")}'
    )
    assert d.get('source') == 'derived_read_only', 'source != derived_read_only'
    assert d.get('runtime_attached') is False, 'runtime_attached deve essere false'
    assert d.get('combat_authoritative') is False, 'combat_authoritative deve essere false'
    assert d.get('reward_authoritative') is False, 'reward_authoritative deve essere false'
    assert d.get('balance_final') is False, 'balance_final deve essere false'
    print('[11] runtime metadata endpoint OK (live, formula+flags coerenti)')
    return 'ok'


def main() -> int:
    check_util_module()
    check_route_module()
    check_read_only()
    check_output_flags()
    check_excluded_sources()
    check_home_no_legacy_power_source()
    check_home_uses_battle_power_hook()
    check_battle_tab_no_account_wide_team()
    check_no_out_of_scope()
    check_pre_qa_safety_suite_registration()
    rt = check_runtime_metadata_endpoint()
    suffix = ' (runtime SKIPPED_BACKEND_DOWN)' if rt == 'skipped' else ''
    print(
        '[v116A PRE_QA_116A_BATTLE_POWER_FOUNDATION] OK '
        'util_module route_module read_only output_flags excluded_sources '
        'home_no_legacy_power home_uses_hook battle_no_account_wide '
        'no_out_of_scope suite_registered runtime_metadata'
        + suffix
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
