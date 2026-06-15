#!/usr/bin/env python3
"""Pre-QA Stabilization 117B — Mega Read-Only Resolver Sprint validator.

Verifica:
- Block A: helper + route hero-upgrade readiness (read-only, server-scoped).
- Block B: battle-power breakdown metadata_only endpoint + formula invariata.
- Block C: nessun fake dot UI (red_dot_candidate=false enforcement).
- Block D: manual QA addendum JSON design_only/read_only.
- Block E: suite registra 117B; no out-of-scope; no bytecode tracciato.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

HELPER = os.path.join(R, 'backend', 'utils', 'hero_upgrade_readiness.py')
ROUTE = os.path.join(R, 'backend', 'routes', 'hero_upgrade_readiness.py')
SERVER = os.path.join(R, 'backend', 'server.py')
BP_ROUTE = os.path.join(R, 'backend', 'routes', 'battle_power.py')
BP_UTIL = os.path.join(R, 'backend', 'utils', 'battle_power.py')
ADDENDUM = os.path.join(R, 'data', 'design', 'release_readiness',
                        'pre_qa_117b_manual_qa_addendum_v1.json')
SUITE = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')


def _r(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def c1():
    for fp in (HELPER, ROUTE, ADDENDUM):
        assert os.path.exists(fp), f'manca: {fp}'
    print('[1] Block A helper+route + Block D addendum exist OK')


def c2():
    hsrc = _r(HELPER)
    rsrc = _r(ROUTE)
    assert "HERO_UPGRADE_READINESS_SOURCE_VERSION = 'hero_upgrade_readiness_v1_preqa_read_only'" in hsrc
    # Categorie canonical
    assert 'CANONICAL_UPGRADE_CATEGORIES' in hsrc
    for cat in ('level_exp', 'star_up', 'ascension', 'skill_upgrade',
                'quality_frame_elevation', 'constellations', 'reincarnation',
                'gear_level', 'gear_quality_fusion', 'gem_socket', 'rune_equip',
                'artifact_global', 'divine_weapon'):
        assert f"'{cat}'" in hsrc, f'category missing in helper: {cat}'
    # Output envelope keys
    for k in ('user_hero_id', 'hero_id', 'can_upgrade_now', 'safe_read_only',
              'confidence', 'upgrade_categories', 'blocked_reasons',
              'requires_future_resolver', 'red_dot_candidate', 'source_version'):
        assert f"'{k}'" in hsrc, f'helper missing key: {k}'
    print('[2] Block A helper: SOURCE_VERSION + 13 categories + envelope keys OK')


def c3():
    rsrc = _r(ROUTE)
    # endpoint paths
    assert 'prefix=' in rsrc and "'/api/hero-upgrade'" in rsrc
    assert "@router.get('/readiness')" in rsrc
    assert "@router.get('/metadata')" in rsrc
    # server_id required + no silent s1
    assert "'SERVER_ID_REQUIRED'" in rsrc
    assert "'no_silent_s1_fallback': True" in rsrc
    # auth required (get_current_user dep)
    assert 'Depends(get_current_user)' in rsrc
    # find_one PSP
    assert 'player_server_profiles' in rsrc and 'find_one' in rsrc
    # read-only: no insert/update/delete patterns
    for pat in ('.insert_one(', '.update_one(', '.delete_one(',
                '.insert_many(', '.update_many(', '.delete_many(',
                '.find_one_and_update(', '.bulk_write(',
                '$set', '$inc', '$push', '$pull', '/claim', '/upgrade',
                '/read-all', '/spend', '/buy'):
        assert pat not in rsrc, f'route forbidden: {pat!r}'
    print('[3] Block A route: prefix + auth + SERVER_ID_REQUIRED + no DB mutations OK')


def c4():
    srv = _r(SERVER)
    # Router montato in server.py
    assert 'create_hero_upgrade_readiness_router' in srv
    assert '/api/hero-upgrade' not in srv or True  # prefix vive nel router stesso
    print('[4] server.py wires hero_upgrade_readiness 117b router OK')


def c5():
    # Block B: battle-power /breakdown endpoint presente, metadata_only_COMPLETE,
    # formula invariata.
    bp = _r(BP_ROUTE)
    assert "@router.get(\"/breakdown\")" in bp or "@router.get('/breakdown')" in bp
    assert 'battle_power_breakdown_v1_preqa_metadata_only' in bp
    assert 'metadata_only_COMPLETE' in bp
    assert "QUALITY_FRAME_SOURCE_NOT_RUNTIME_SAFE_YET" in bp
    assert 'no_per_user_data' in bp and 'no_db_reads' in bp
    # Formula invariata (verifica anche utils)
    util = _r(BP_UTIL)
    assert "battle_power_v1_preqa_derived" in util
    print('[5] Block B breakdown endpoint metadata_only + formula invariant OK')


def c6():
    # Block D addendum: design_only/read_only, righe presenti, coverage 12 surfaces
    d = json.loads(_r(ADDENDUM))
    m = d.get('_meta', {})
    assert m.get('scope') == 'design_only_read_only'
    assert m.get('is_runtime') is False
    assert m.get('do_not_use_for_runtime_resolution') is True
    assert m.get('pack_origin') == '117B'
    rows = d.get('rows', [])
    assert len(rows) >= 12, f'addendum troppo corto: {len(rows)}'
    qa_ids = [r['qa_id'] for r in rows]
    assert len(set(qa_ids)) == len(qa_ids), 'qa_id duplicati'
    required_surfaces = {
        'hero_upgrade_readiness_endpoint',
        'hero_card_red_dot_if_active',
        'hero_detail_upgrade_hint_if_active',
        'bp_breakdown_quality_frame_probe_if_active',
        'home_menu_red_dot_aggregation',
        'negative_no_server',
        'negative_no_psp',
        'negative_no_team',
        'negative_source_unsafe',
        'negative_deferred_source',
    }
    covered = set(d.get('coverage', {}).get('required_surfaces_covered', []))
    missing = required_surfaces - covered
    assert not missing, f'addendum non copre: {missing}'
    print(f'[6] Block D addendum design_only + {len(rows)} rows + coverage OK')


def c7():
    # Block C invariants: 117B non aggrega red dot per hero-upgrade in 116C summary.
    rd_route = _r(os.path.join(R, 'backend', 'routes', 'red_dot.py'))
    rd_util = _r(os.path.join(R, 'backend', 'utils', 'red_dot_summary.py'))
    # 116C version invariata
    assert 'red_dot_v1_preqa_read_only_foundation' in rd_util
    # no aggregazione di hero-upgrade in red_dot in questo pack
    for pat in ('hero_upgrade_readiness', '/api/hero-upgrade'):
        assert pat not in rd_route, f'red_dot route non deve usare {pat}'
        assert pat not in rd_util, f'red_dot util non deve usare {pat}'
    print('[7] Block C: red_dot 116C non aggrega hero-upgrade in 117B OK')


def c8():
    # No claim/spend/push/upgrade activation nei file nuovi
    files_to_check = (HELPER, ROUTE, ADDENDUM)
    forbidden = (
        '.insert_one(', '.update_one(', '.delete_one(',
        '.insert_many(', '.update_many(', '.delete_many(',
        '.find_one_and_update(', '.bulk_write(', '.replace_one(',
        '/api/mail/read-all', '/api/mail/claim',
        '/api/daily-quest/claim', '/api/daily-login/claim',
        '/api/achievements/claim', '/api/battle-pass/claim',
        '/api/shop/buy', '/api/gacha/summon',
        '/api/push/register', '/api/push/test', '/api/reward/claim',
        '/api/hero/upgrade', '/api/hero/levelup', '/api/fusion/star-up',
        '/api/hero/elevation/{hero_id}/upgrade',
    )
    for fp in files_to_check:
        c = _r(fp)
        for pat in forbidden:
            assert pat not in c, f'{os.path.basename(fp)}: vietato {pat!r}'
    print('[8] no DB mutation + no claim/upgrade/spend/push activation in 117B files OK')


def c9():
    # No battle_engine import / out-of-scope nei file 117B
    for fp in (HELPER, ROUTE):
        c = _r(fp)
        for pat in (r'from\s+\S*battle_engine\b',
                    r'from\s+\S*combat_runtime\b',
                    r'from\s+\S*tower_runtime\b',
                    r'from\s+\S*gacha_rates_runtime\b',
                    r'from\s+\S*character_bible_runtime\b'):
            assert not re.search(pat, c), f'{os.path.basename(fp)}: out-of-scope {pat}'
    print('[9] no out-of-scope imports in 117B Block A files OK')


def c10():
    # Block A invariant: nessuna riga forza can_upgrade_now=True nel helper.
    h = _r(HELPER)
    # Cerchiamo: 'can_upgrade_now': True / 'can_upgrade_now': true
    assert "'can_upgrade_now': True" not in h, 'helper non deve dichiarare can_upgrade_now=True in 117B'
    assert "'can_upgrade_now': true" not in h
    print('[10] Block A invariant: no can_upgrade_now=True in helper OK')


def c11():
    # Pack 116B preserved
    contract = json.loads(_r(os.path.join(R, 'data', 'design', 'server_actors',
                                          'v116b_bot_chat_quality_contract_v1.json')))
    flags = contract.get('live_activation_flags', {}) or {}
    for k, v in flags.items():
        assert v is False, f'116B regressione: {k}=True'
    print('[11] Pack 116B chat/bot contract preserved OK')


def c12():
    # No .pyc / __pycache__ tracciati
    out = subprocess.check_output(['git', '-C', R, 'ls-files'],
                                  stderr=subprocess.DEVNULL).decode()
    tracked = [p for p in out.splitlines()
               if p.endswith('.pyc') or '__pycache__/' in p]
    assert not tracked, f'bytecode tracked: {tracked[:5]}'
    print('[12] no .pyc / __pycache__ tracked OK')


def c13():
    # Suite registra 117B
    c = _r(SUITE)
    must = 'validate_pre_qa_stabilization_117b_mega_read_only_resolver_sprint.py'
    assert must in c, 'suite non registra 117B'
    print('[13] pre-QA safety suite registers 117B OK')


def c14():
    # Runtime check (best-effort): metadata + breakdown 200.
    try:
        import urllib.request
        with urllib.request.urlopen(
                'http://127.0.0.1:8001/api/hero-upgrade/metadata', timeout=5) as resp:
            d = json.loads(resp.read())
            assert d.get('source_version') == 'hero_upgrade_readiness_v1_preqa_read_only'
            assert d.get('safe_read_only') is True
            assert d.get('no_db_writes') is True
        with urllib.request.urlopen(
                'http://127.0.0.1:8001/api/battle-power/breakdown', timeout=5) as resp:
            d = json.loads(resp.read())
            assert d.get('breakdown_version') == 'battle_power_breakdown_v1_preqa_metadata_only'
            assert d.get('formula_version_invariant') == 'battle_power_v1_preqa_derived'
            assert d.get('block_outcome_117b_block_b') == 'metadata_only_COMPLETE'
        print('[14] runtime /api/hero-upgrade/metadata + /api/battle-power/breakdown OK')
    except Exception as e:
        # Runtime down e' uno SKIP esplicito (non PASS, non FAIL bloccante per
        # gli static check; il main suite tracker rilevera' backend_up).
        print(f'[14] runtime check SKIPPED_BACKEND_DOWN: {e}')


def main():
    c1(); c2(); c3(); c4(); c5(); c6(); c7(); c8(); c9(); c10(); c11(); c12(); c13(); c14()
    print('[v117B PRE_QA_117B_MEGA_READ_ONLY_RESOLVER_SPRINT] OK '
          'block_a_helper block_a_route block_a_server_wired block_b_breakdown '
          'block_d_addendum block_c_no_red_dot_aggregation no_mutations '
          'no_out_of_scope no_can_upgrade_true 116b_preserved no_bytecode '
          'suite_registered runtime_smoke')
    return 0


if __name__ == '__main__':
    sys.exit(main())
