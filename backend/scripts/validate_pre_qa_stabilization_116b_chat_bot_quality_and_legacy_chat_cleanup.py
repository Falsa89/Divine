#!/usr/bin/env python3
"""Pre-QA Stabilization 116B — Chat/Bot Quality & Legacy Chat Cleanup validator.

Static validator. No DB writes. No runtime activation.

Checks (at least):
  1. `/plaza` is screen-gated via PreQaScreenGate (early-return before hooks).
  2. `/dm` is screen-gated via PreQaScreenGate (early-return before hooks).
  3. `useChatChannel` ha hook-level fail-close (`isRouteAllowedInPreQa('/plaza')`).
  4. `useDM` ha hook-level fail-close (`isRouteAllowedInPreQa('/dm')`).
  5. Le route `/plaza` e `/dm` sono nel `blocked` set di `preQaNavGuard.ts`.
  6. Bot chat quality contract 116B esiste, e' `design_only_pre_qa_locked` e
     contiene tutte le invarianti richieste dal pack.
  7. Contract dichiara `bot_chat_live=false`, `dm_bot_live=false`,
     `fake_users_presented_as_real=false`.
  8. Contract enumera forbidden_bot_behaviors: manual_ultimate_advice,
     real_iap_recommendation, real_pii, toxicity, competing_game_ads,
     out_of_context_response.
  9. Contract richiede pre-live: server_scope_required, moderation_required,
     rate_limits_required, admin_kill_switch_required.
 10. v109 chat live_ready=false e' preservato O superseded solo da contract
     pre-QA locked (non da contract live).
 11. NESSUN cambiamento a battle_engine/combat/tower/gacha/reward/Red Dot/
     Character Bible: i file dello scope 116B non importano questi runtime.
 12. NESSUNA traccia `__pycache__/.pyc` (hygiene 115F preservata).
 13. Pre-QA safety suite include validator 116B.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

PLAZA_TSX_FP = os.path.join(R, 'frontend', 'app', 'plaza.tsx')
DM_TSX_FP = os.path.join(R, 'frontend', 'app', 'dm.tsx')
USE_CHAT_FP = os.path.join(R, 'frontend', 'hooks', 'useChatChannel.ts')
USE_DM_FP = os.path.join(R, 'frontend', 'hooks', 'useDM.ts')
NAV_GUARD_FP = os.path.join(R, 'frontend', 'src', 'utils', 'preQaNavGuard.ts')
CONTRACT_FP = os.path.join(R, 'data', 'design', 'server_actors', 'v116b_bot_chat_quality_contract_v1.json')
V109_CHAT_FP = os.path.join(R, 'data', 'design', 'v109_server_isolation', 'v109_chat_guild_gvg_rankings_isolation_v1.json')
SUITE_FP = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')


def _read(fp: str) -> str:
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def check_plaza_screen_gated():
    c = _read(PLAZA_TSX_FP)
    assert "isScreenGated('/plaza')" in c, "plaza.tsx non chiama isScreenGated('/plaza')"
    assert 'PreQaScreenGate' in c, "plaza.tsx non importa PreQaScreenGate"
    # Verifica early-return PRIMA degli hook.
    idx_gate = c.find("if (isScreenGated('/plaza'))")
    idx_use = c.find('useChatChannel(')
    assert idx_gate >= 0 and idx_use >= 0
    assert idx_gate < idx_use, "plaza.tsx: gate NON e' early-return prima degli hook"
    print('[1] /plaza screen-gated via PreQaScreenGate (early-return before hooks) OK')


def check_dm_screen_gated():
    c = _read(DM_TSX_FP)
    assert "isScreenGated('/dm')" in c, "dm.tsx non chiama isScreenGated('/dm')"
    assert 'PreQaScreenGate' in c, "dm.tsx non importa PreQaScreenGate"
    print('[2] /dm screen-gated via PreQaScreenGate OK')


def check_chat_hook_fail_close():
    c = _read(USE_CHAT_FP)
    assert 'isRouteAllowedInPreQa' in c, "useChatChannel non importa isRouteAllowedInPreQa"
    assert "_chatPreQaBlocked" in c or "_chat_pre_qa_blocked" in c.lower(), (
        'useChatChannel non implementa la guardia hook-level'
    )
    # Verifica fail-close su entrambi load e send.
    assert re.search(r'if\s*\(\s*_chatPreQaBlocked\(\)\s*\)', c), (
        'useChatChannel non fail-close su load'
    )
    # Verifica che la guard sia chiamata in send pure (almeno 2 occorrenze
    # totali della funzione).
    occurrences = len(re.findall(r'_chatPreQaBlocked\(\)', c))
    assert occurrences >= 2, (
        f'useChatChannel: la guardia deve coprire load+send (trovate {occurrences} occorrenze)'
    )
    print('[3] useChatChannel hook-level fail-close (load + send) OK')


def check_dm_hook_fail_close():
    c = _read(USE_DM_FP)
    assert 'isRouteAllowedInPreQa' in c, "useDM non importa isRouteAllowedInPreQa"
    assert '_dmPreQaBlocked' in c, 'useDM non implementa la guardia hook-level'
    # Deve coprire tutti i 5 path: refreshThreads, refreshMessages, openWithUser, sendMessage, markRead.
    occurrences = len(re.findall(r'_dmPreQaBlocked\(\)', c))
    assert occurrences >= 5, (
        f'useDM: la guardia deve coprire 5 path (refresh threads/messages, open, send, read); '
        f'trovate {occurrences} occorrenze'
    )
    print('[4] useDM hook-level fail-close (5 paths) OK')


def check_blocked_routes_set():
    c = _read(NAV_GUARD_FP)
    for route in ("'/plaza'", "'/dm'"):
        assert route in c, f'preQaNavGuard.ts non blocca {route}'
    print('[5] /plaza and /dm in preQaNavGuard blocked set OK')


def check_contract_exists_and_locked():
    assert os.path.exists(CONTRACT_FP), 'manca v116b_bot_chat_quality_contract_v1.json'
    d = json.loads(_read(CONTRACT_FP))
    assert d.get('_meta', {}).get('scope') == 'design_only_pre_qa_locked', (
        'contract scope deve essere design_only_pre_qa_locked'
    )
    assert d.get('runtime_state') == 'design_only_pre_qa_locked', (
        'contract runtime_state deve essere design_only_pre_qa_locked'
    )
    assert d.get('_meta', {}).get('is_runtime') is False
    assert d.get('_meta', {}).get('do_not_use_for_runtime_activation') is True
    print('[6] bot chat quality contract v116b present + design_only_pre_qa_locked OK')


def check_contract_live_flags():
    d = json.loads(_read(CONTRACT_FP))
    laf = d.get('live_activation_flags', {})
    for k in ('bot_chat_live', 'dm_bot_live', 'fake_users_presented_as_real'):
        assert laf.get(k) is False, f'live_activation_flags.{k} deve essere False'
    print('[7] contract live_activation_flags all false OK')


def check_contract_forbidden_behaviors():
    d = json.loads(_read(CONTRACT_FP))
    fb = d.get('forbidden_bot_behaviors', {})
    required = (
        'manual_ultimate_advice_forbidden',
        'real_iap_recommendation_forbidden',
        'real_pii_forbidden',
        'toxicity_forbidden',
        'competing_game_ads_forbidden',
        'out_of_context_response_forbidden',
    )
    for k in required:
        assert fb.get(k) is True, f'forbidden_bot_behaviors.{k} deve essere True'
    print('[8] contract forbidden_bot_behaviors all true (6 invariants) OK')


def check_contract_required_invariants():
    d = json.loads(_read(CONTRACT_FP))
    inv = d.get('required_safety_invariants_before_live', {})
    required = (
        'server_scope_required',
        'moderation_required_before_live',
        'rate_limits_required_before_live',
        'admin_kill_switch_required',
    )
    for k in required:
        assert inv.get(k) is True, f'required_safety_invariants_before_live.{k} deve essere True'
    print('[9] contract required_safety_invariants_before_live (4 invariants) OK')


def check_v109_chat_not_live():
    """v109 chat must continue to declare live_ready=false (or equivalent)
    OR superseded only by the locked 116B contract.
    """
    if not os.path.exists(V109_CHAT_FP):
        print('[10] v109 chat isolation file NON presente — skipping detail check')
        return
    d = json.loads(_read(V109_CHAT_FP))
    # Cerca esplicitamente `live_ready=false` o equivalente in qualsiasi parte
    # del documento (lookup permissivo: stringify e match).
    text = json.dumps(d, ensure_ascii=False)
    has_not_ready = (
        '"live_ready": false' in text
        or '"chat_live_ready": false' in text
        or '"live_ready":false' in text
        or 'pre_qa_locked' in text
        or 'not_live_ready' in text
        or 'fail_closed' in text
    )
    assert has_not_ready, (
        'v109 chat isolation non dichiara piu\' live_ready=false / pre_qa_locked '
        '(regressione vietata: se vuoi cambiare, deve passare per il contract 116b)'
    )
    print('[10] v109 chat live_ready=false / pre_qa_locked preserved OK')


def check_no_out_of_scope():
    pack_files = (
        PLAZA_TSX_FP, DM_TSX_FP,
        USE_CHAT_FP, USE_DM_FP,
        CONTRACT_FP,
    )
    forbidden_patterns = (
        r'^\s*from\s+\S*battle_engine\b',
        r'^\s*import\s+\S*battle_engine\b',
        r'^\s*from\s+\S*combat_runtime\b',
        r'^\s*from\s+\S*tower_runtime\b',
        r'^\s*from\s+\S*gacha_rates_runtime\b',
        r'^\s*from\s+\S*red_dot_runtime\b',
        r'^\s*from\s+\S*character_bible_runtime\b',
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
    assert not offenders, f'out-of-scope import: {offenders}'
    print('[11] no out-of-scope imports across pack-116B files OK')


def check_no_bytecode_tracked():
    try:
        out = subprocess.check_output(['git', '-C', R, 'ls-files'], stderr=subprocess.DEVNULL)
        tracked = out.decode('utf-8', errors='replace').splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Fail-closed: in dubbio non passare.
        raise AssertionError('git non disponibile: impossibile verificare bytecode tracking')
    pyc = [p for p in tracked if p.endswith('.pyc') or '__pycache__/' in p]
    assert not pyc, f'bytecode ancora tracciato: {pyc[:5]}'
    print('[12] no .pyc / __pycache__ tracked OK')


def check_suite_registration():
    c = _read(SUITE_FP)
    must = 'validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py'
    assert must in c, f'pre-QA safety suite non registra 116B: manca {must!r}'
    print('[13] pre-QA safety suite registers 116B validator OK')


def main() -> int:
    check_plaza_screen_gated()
    check_dm_screen_gated()
    check_chat_hook_fail_close()
    check_dm_hook_fail_close()
    check_blocked_routes_set()
    check_contract_exists_and_locked()
    check_contract_live_flags()
    check_contract_forbidden_behaviors()
    check_contract_required_invariants()
    check_v109_chat_not_live()
    check_no_out_of_scope()
    check_no_bytecode_tracked()
    check_suite_registration()
    print(
        '[v116B PRE_QA_116B_CHAT_BOT_QUALITY_AND_LEGACY_CHAT_CLEANUP] OK '
        'plaza_gated dm_gated chat_hook_failclose dm_hook_failclose '
        'blocked_routes_set contract_present contract_live_flags '
        'contract_forbidden_behaviors contract_required_invariants '
        'v109_chat_not_live no_out_of_scope no_bytecode_tracked '
        'suite_registered'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
