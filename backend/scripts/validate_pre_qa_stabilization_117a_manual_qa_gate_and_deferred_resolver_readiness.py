#!/usr/bin/env python3
"""Pre-QA Stabilization 117A — Manual QA Gate & Deferred Resolver Readiness validator.

Diagnostico/read-only. NON attiva alcun resolver, NON modifica formula BP / RD.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')
QA_MATRIX = os.path.join(R, 'data', 'design', 'release_readiness',
                         'pre_qa_117a_manual_qa_gate_matrix_v1.json')
BP_READINESS = os.path.join(R, 'data', 'design', 'battle_power',
                            'deferred_power_resolver_readiness_v1.json')
RD_READINESS = os.path.join(R, 'data', 'design', 'red_dot',
                            'deferred_red_dot_resolver_readiness_v1.json')
BP_SOURCE_MAP = os.path.join(R, 'data', 'design', 'battle_power',
                             'battle_power_bonus_source_map_v1.json')
RD_SOURCE_MAP = os.path.join(R, 'data', 'design', 'red_dot',
                             'red_dot_notification_badge_source_map_v1.json')
SUITE = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

ALLOWED_BANDS = {
    'safe_read_only_resolver_candidate',
    'design_ready_runtime_blocked',
    'requires_backend_contract',
    'requires_economy_or_balance_gate',
    'requires_manual_design_confirmation',
    'not_ready',
}


def _r(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def c1():
    for fp in (QA_MATRIX, BP_READINESS, RD_READINESS):
        assert os.path.exists(fp), f'manca: {fp}'
        json.loads(_r(fp))  # valid JSON
    print('[1] 3 JSON exist and parse OK')


def c2():
    for fp in (QA_MATRIX, BP_READINESS, RD_READINESS):
        d = json.loads(_r(fp))
        m = d.get('_meta', {})
        assert m.get('scope') == 'design_only_read_only', fp
        assert m.get('is_runtime') is False, fp
        assert m.get('do_not_use_for_runtime_resolution') is True, fp
        assert m.get('pack_origin') == '117A', fp
    print('[2] design_only / read_only / pack_origin=117A OK')


def c3():
    d = json.loads(_r(QA_MATRIX))
    rows = d.get('rows', [])
    assert len(rows) >= 12, f'matrix troppo corta: {len(rows)}'
    required_fields = {'qa_id', 'area', 'surface', 'route_or_endpoint',
                       'source_of_truth', 'expected_state',
                       'expected_player_visible_copy_or_signal',
                       'runtime_required_for_manual_qa', 'safe_to_test_now',
                       'blocked_by_pre_qa', 'severity_if_failed', 'notes'}
    for r in rows:
        missing = required_fields - set(r.keys())
        assert not missing, f'row {r.get("qa_id")} manca: {missing}'
    qa_ids = [r['qa_id'] for r in rows]
    assert len(set(qa_ids)) == len(qa_ids), 'qa_id duplicati'
    print(f'[3] manual QA matrix rows={len(rows)} required_fields present OK')


def c4():
    d = json.loads(_r(QA_MATRIX))
    cov = d.get('coverage', {})
    required_surfaces = {
        'home_bp_display',
        'home_red_dot_display',
        'menu_red_dot_display',
        'heroes_card_power_badge',
        'hero_detail_power_display',
        'battle_formation_slot_index',
        'battle_power_summary_metadata',
        'red_dot_summary_metadata',
        'plaza_dm_locked',
        'gacha_shop_battlepass_mail_daily_event_locked_or_deferred',
        'server_profile_warning',
        'team_missing_warning',
    }
    covered = set(cov.get('required_surfaces_covered', []))
    missing = required_surfaces - covered
    assert not missing, f'manual QA matrix non copre: {missing}'
    print('[4] manual QA matrix covers all 12 required surfaces OK')


def c5():
    src_map = json.loads(_r(BP_SOURCE_MAP))
    deferred_ids = {e['source_id'] for e in src_map.get('deferred_canonical_power_sources', [])
                    if isinstance(e, dict)}
    rd = json.loads(_r(BP_READINESS))
    rd_ids = {e['source_id'] for e in rd.get('deferred_resolvers', [])}
    missing = deferred_ids - rd_ids
    assert not missing, f'BP readiness non classifica: {missing}'
    # tutti i band validi e flag invariant
    for e in rd['deferred_resolvers']:
        assert e.get('readiness_band') in ALLOWED_BANDS, f'banda invalida: {e}'
        assert e.get('can_affect_battle_power_now') is False, \
            f'BP attivazione vietata: {e["source_id"]}'
        for k in ('recommended_pack', 'blocking_requirements',
                  'required_validator_checks', 'source_refs', 'notes'):
            assert k in e, f'BP readiness {e["source_id"]} manca {k}'
    print(f'[5] BP readiness classifies all {len(deferred_ids)} deferred + invariants OK')


def c6():
    rd_map = json.loads(_r(RD_SOURCE_MAP))
    deferred_ids = set()
    for sect in ('locked_or_deferred_sources', 'future_resolver_sources',
                 'non_actionable_system_warning_sources',
                 'unknown_requires_source_confirmation'):
        for e in rd_map.get(sect, []):
            if isinstance(e, dict) and 'source_id' in e:
                deferred_ids.add(e['source_id'])
    rd = json.loads(_r(RD_READINESS))
    rd_ids = {e['source_id'] for e in rd.get('deferred_resolvers', [])}
    missing = deferred_ids - rd_ids
    assert not missing, f'RD readiness non classifica: {missing}'
    for e in rd['deferred_resolvers']:
        assert e.get('readiness_band') in ALLOWED_BANDS, f'banda invalida RD: {e}'
        assert e.get('can_show_actionable_dot_now') is False, \
            f'RD dot actionable vietato per deferred: {e["source_id"]}'
        for k in ('recommended_pack', 'blocking_requirements',
                  'mutation_risk', 'source_refs', 'notes'):
            assert k in e, f'RD readiness {e["source_id"]} manca {k}'
    # warning gia' attive preservate
    active = rd.get('active_safe_warnings_preserved_from_116c', [])
    active_ids = {e['source_id'] for e in active}
    assert {'server_profile_required', 'team_missing_warning'} <= active_ids
    print(f'[6] RD readiness classifies all {len(deferred_ids)} deferred + 116C warnings preserved OK')


def c7():
    # invariant aggregata: nessuna sorgente deferred puo' essere "active" nei JSON 117A
    rd_bp = json.loads(_r(BP_READINESS))
    for e in rd_bp['deferred_resolvers']:
        assert e['can_affect_battle_power_now'] is False
    rd_rd = json.loads(_r(RD_READINESS))
    for e in rd_rd['deferred_resolvers']:
        assert e['can_show_actionable_dot_now'] is False
    print('[7] no live activation across 117A JSONs OK')


def c8():
    # Nessun DB write / claim / mutation pattern nei JSON 117A (i 3 JSON sono
    # design-only e non devono contenere chiamate endpoint claim/read-all).
    files_to_check = (QA_MATRIX, BP_READINESS, RD_READINESS)
    forbidden_substrings = (
        '.insert_one(', '.update_one(', '.delete_one(',
        '.insert_many(', '.update_many(', '.delete_many(',
        '.find_one_and_update(', '.bulk_write(', '.replace_one(',
        '/api/mail/read-all', '/api/mail/claim',
        '/api/daily-quest/claim', '/api/daily-login/claim',
        '/api/achievements/claim', '/api/battle-pass/claim',
        '/api/shop/buy', '/api/gacha/summon',
        '/api/push/register', '/api/push/test', '/api/reward/claim',
    )
    for fp in files_to_check:
        c = _r(fp)
        for pat in forbidden_substrings:
            assert pat not in c, f'{os.path.basename(fp)}: vietato {pat!r}'
    print('[8] no DB mutation patterns + no claim/read-all/spend/push activation OK')


def c9():
    # nessun import di battle_engine / combat_runtime / tower_runtime nei
    # file 117A (nessun file Python del pack a parte questo validator).
    me = _r(os.path.abspath(__file__))
    for pat in (r'^\s*from\s+\S*battle_engine\b',
                r'^\s*from\s+\S*combat_runtime\b',
                r'^\s*from\s+\S*tower_runtime\b',
                r'^\s*from\s+\S*gacha_rates_runtime\b',
                r'^\s*from\s+\S*character_bible_runtime\b'):
        assert not re.search(pat, me, re.MULTILINE), f'validator: out-of-scope {pat}'
    print('[9] validator 117A no out-of-scope imports OK')


def c10():
    # Pack 116B preservato: bot quality contract live_ready=false.
    contract_fp = os.path.join(R, 'data', 'design', 'server_actors',
                               'v116b_bot_chat_quality_contract_v1.json')
    c = json.loads(_r(contract_fp))
    flags = c.get('live_activation_flags', {}) or {}
    for k, v in flags.items():
        assert v is False, f'116B regressione: {k}=True'
    print('[10] 116B chat/bot contract preserved (all live_activation_flags false) OK')


def c11():
    # Battle Power formula version invariata.
    util_fp = os.path.join(R, 'backend', 'utils', 'battle_power.py')
    c = _r(util_fp)
    assert 'battle_power_v1_preqa_derived' in c, 'BP formula version cambiata'
    # 117A non deve avere modificato BP util.
    print('[11] battle_power formula_version invariant OK')


def c12():
    # Red Dot summary version invariata.
    util_fp = os.path.join(R, 'backend', 'utils', 'red_dot_summary.py')
    c = _r(util_fp)
    assert 'red_dot_v1_preqa_read_only_foundation' in c, 'RD version cambiata'
    print('[12] red_dot_summary version invariant OK')


def c13():
    # no .pyc / __pycache__ tracciati.
    out = subprocess.check_output(['git', '-C', R, 'ls-files'],
                                  stderr=subprocess.DEVNULL).decode()
    tracked = [p for p in out.splitlines()
               if p.endswith('.pyc') or '__pycache__/' in p]
    assert not tracked, f'bytecode tracked: {tracked[:5]}'
    print('[13] no .pyc / __pycache__ tracked OK')


def c14():
    c = _r(SUITE)
    must = 'validate_pre_qa_stabilization_117a_manual_qa_gate_and_deferred_resolver_readiness.py'
    assert must in c, 'suite non registra 117A'
    print('[14] pre-QA safety suite registers 117A OK')


def main():
    c1(); c2(); c3(); c4(); c5(); c6(); c7(); c8(); c9(); c10(); c11(); c12(); c13(); c14()
    print('[v117A PRE_QA_117A_MANUAL_QA_GATE_AND_DEFERRED_RESOLVER_READINESS] OK '
          'json_present design_only_meta matrix_required_fields surfaces_coverage '
          'bp_readiness_complete rd_readiness_complete no_live_activation '
          'no_db_mutations_no_claims no_out_of_scope_imports '
          'pack116b_preserved bp_formula_invariant rd_version_invariant '
          'no_bytecode_tracked suite_registered')
    return 0


if __name__ == '__main__':
    sys.exit(main())
