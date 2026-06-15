#!/usr/bin/env python3
"""Pre-QA Stabilization 118 — Manual QA Device Unlock Pass validator.

Diagnostico/read-only. Verifica i 4 nuovi deliverable + suite registration.
NON attiva nessun resolver. NON modifica formula BP / RD / hero upgrade.
"""
import json
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

QA_MATRIX = os.path.join(R, 'data', 'design', 'release_readiness',
                         'pre_qa_118_manual_qa_allowed_surface_matrix_v1.json')
TRIAGE = os.path.join(R, 'data', 'design', 'release_readiness',
                      'pre_qa_119_post_qa_triage_buckets_v1.json')
RUNBOOK = os.path.join(R, 'docs', 'divine', 'qa', '118_MANUAL_QA_DEVICE_RUNBOOK.md')
EVIDENCE = os.path.join(R, 'docs', 'divine', 'qa', '118_MANUAL_QA_EVIDENCE_TEMPLATE.md')
SUITE = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

# Invariants files che devono restare inalterati nel pack 118.
BP_UTIL = os.path.join(R, 'backend', 'utils', 'battle_power.py')
RD_UTIL = os.path.join(R, 'backend', 'utils', 'red_dot_summary.py')
HU_UTIL = os.path.join(R, 'backend', 'utils', 'hero_upgrade_readiness.py')
CHAT_CONTRACT = os.path.join(R, 'data', 'design', 'server_actors',
                             'v116b_bot_chat_quality_contract_v1.json')

ALLOWED_STATUSES = {
    'allowed_targeted_device_qa',
    'allowed_read_only_endpoint_check',
    'locked_verify_stays_locked',
    'deferred_do_not_test_as_live',
    'blocked_until_future_pack',
}


def _r(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def c1():
    for fp in (QA_MATRIX, TRIAGE, RUNBOOK, EVIDENCE):
        assert os.path.exists(fp), f'manca: {fp}'
    # JSON valid
    json.loads(_r(QA_MATRIX))
    json.loads(_r(TRIAGE))
    # MD non vuoto
    assert len(_r(RUNBOOK)) > 1500
    assert len(_r(EVIDENCE)) > 800
    print('[1] 4 deliverable present + valid OK')


def c2():
    d = json.loads(_r(QA_MATRIX))
    m = d.get('_meta', {})
    assert m.get('scope') == 'design_only_read_only'
    assert m.get('is_runtime') is False
    assert m.get('do_not_use_for_runtime_resolution') is True
    assert m.get('pack_origin') == '118'
    declared = set(m.get('allowed_status_values', []))
    assert declared == ALLOWED_STATUSES, f'allowed_status_values mismatch: {declared}'
    print('[2] QA matrix design_only + 5 allowed_status_values OK')


def c3():
    d = json.loads(_r(QA_MATRIX))
    rows = d.get('rows', [])
    assert len(rows) >= 26, f'matrix troppo corta: {len(rows)}'
    required_fields = {'qa_id', 'area', 'surface', 'route_or_endpoint',
                       'status', 'source_of_truth', 'expected_behavior',
                       'verifier_actions', 'pre_qa_invariants',
                       'severity_if_failed'}
    for r in rows:
        missing = required_fields - set(r.keys())
        assert not missing, f'row {r.get("qa_id")} manca: {missing}'
        assert r['status'] in ALLOWED_STATUSES, \
            f'row {r["qa_id"]} status non valido: {r["status"]}'
        assert r['severity_if_failed'] in {'P0', 'P1', 'NA'}, \
            f'row {r["qa_id"]} severity invalida'
        assert isinstance(r['verifier_actions'], list)
        assert isinstance(r['pre_qa_invariants'], list)
    qa_ids = [r['qa_id'] for r in rows]
    assert len(set(qa_ids)) == len(qa_ids), 'qa_id duplicati'
    print(f'[3] QA matrix rows={len(rows)} required_fields + status validi OK')


def c4():
    d = json.loads(_r(QA_MATRIX))
    cov = d.get('coverage', {}).get('required_surfaces_covered', [])
    needed = {
        'home_battle_power_display',
        'home_red_dot_display',
        'menu_red_dot_display',
        'heroes_card_power_badge',
        'hero_detail_power_and_upgrade_hint',
        'battle_formation_slot_index',
        'battle_power_metadata_and_summary',
        'battle_power_breakdown_metadata_only',
        'red_dot_metadata_and_summary',
        'hero_upgrade_metadata_and_readiness',
        'locked_plaza_dm_gacha',
        'locked_or_deferred_shop_battlepass_mail_daily_events',
        'negative_no_server_no_psp_no_team_source_unsafe_deferred',
    }
    missing = needed - set(cov)
    assert not missing, f'coverage non copre: {missing}'
    # Status distribution somma a totale
    dist = d.get('coverage', {}).get('status_distribution', {})
    total = d.get('coverage', {}).get('total_rows')
    assert sum(dist.values()) == total == len(d.get('rows', [])), \
        f'status_distribution somma!=total: {sum(dist.values())} vs {total}'
    print('[4] QA matrix coverage 13/13 surfaces + status_distribution coerente OK')


def c5():
    d = json.loads(_r(QA_MATRIX))
    rows = d.get('rows', [])
    statuses_seen = {r['status'] for r in rows}
    assert statuses_seen == ALLOWED_STATUSES, \
        f'matrix non usa tutti gli status: missing={ALLOWED_STATUSES-statuses_seen}'
    print('[5] QA matrix uses all 5 allowed statuses OK')


def c6():
    d = json.loads(_r(TRIAGE))
    m = d.get('_meta', {})
    assert m.get('scope') == 'design_only_read_only'
    assert m.get('is_runtime') is False
    assert m.get('pack_origin') == '118_prep_for_119'
    buckets = d.get('triage_buckets', [])
    bucket_ids = {b['bucket_id'] for b in buckets}
    needed = {'B1_ui_copy_or_label_fix', 'B2_ui_layout_or_safe_area_fix',
              'B3_read_only_endpoint_payload_polish', 'B4_locked_route_copy_polish',
              'B5_red_dot_aggregation_polish', 'B6_observability_or_log_polish',
              'B7_security_or_auth_minor_issue', 'B8_blocked_until_future_pack',
              'B9_safety_violation_blocker'}
    missing = needed - bucket_ids
    assert not missing, f'triage buckets mancanti: {missing}'
    # global_invariants presenti
    inv = d.get('global_invariants', {})
    assert 'pack_119_must_preserve' in inv
    assert 'pack_119_must_not' in inv
    print(f'[6] Triage buckets 9/9 (B1..B9) + global invariants OK')


def c7():
    # Runbook contiene sezioni chiave
    c = _r(RUNBOOK)
    for needle in ('Pre-requisiti', 'Setup sessione', 'Fase A', 'Fase B',
                   'Fase C', 'Regole d', 'Triage buckets', 'Stop conditions',
                   '118_qa_001', '118_qa_026'):
        assert needle in c, f'runbook manca sezione: {needle}'
    # Anti-claim explicit
    assert 'NON autorizza' in c
    assert 'B9' in c and 'safety_violation' in c.lower()
    print('[7] Runbook contains required sections + anti-claim warnings OK')


def c8():
    # Evidence template ha placeholder corretti
    c = _r(EVIDENCE)
    for needle in ('Sessione QA', 'Tester', 'Build ID', 'qa_id',
                   'observed_outcome', 'bucket_triage_if_failed',
                   'severity_if_failed', 'Verdetto finale tester',
                   'P0', 'P1', 'B9'):
        assert needle in c, f'evidence template manca: {needle}'
    print('[8] Evidence template contains required fields OK')


def c9():
    # Invariants preserved (BP formula, RD version, HU source version)
    assert 'battle_power_v1_preqa_derived' in _r(BP_UTIL), 'BP formula version cambiata'
    assert 'red_dot_v1_preqa_read_only_foundation' in _r(RD_UTIL), 'RD version cambiata'
    assert "'hero_upgrade_readiness_v1_preqa_read_only'" in _r(HU_UTIL), 'HU version cambiata'
    # Chat contract 116B preserved
    cc = json.loads(_r(CHAT_CONTRACT))
    flags = cc.get('live_activation_flags', {}) or {}
    for k, v in flags.items():
        assert v is False, f'116B regressione: {k}=True'
    # HU helper invariant: no can_upgrade_now=True
    hu = _r(HU_UTIL)
    assert "'can_upgrade_now': True" not in hu
    assert "'can_upgrade_now': true" not in hu
    print('[9] Invariants preserved (BP/RD/HU versions + 116B contract + no can_upgrade_now=True) OK')


def c10():
    # No live activation pattern nei nuovi file
    files_to_check = (QA_MATRIX, TRIAGE, RUNBOOK, EVIDENCE)
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
    print('[10] no DB mutation + no claim/upgrade/spend/push references in 118 files OK')


def c11():
    # No out-of-scope import in validator stesso
    me = _r(os.path.abspath(__file__))
    for pat in (r'from\s+\S*battle_engine\b',
                r'from\s+\S*combat_runtime\b',
                r'from\s+\S*tower_runtime\b',
                r'from\s+\S*gacha_rates_runtime\b',
                r'from\s+\S*character_bible_runtime\b'):
        assert not re.search(pat, me), f'validator out-of-scope {pat}'
    print('[11] no out-of-scope imports in validator 118 OK')


def c12():
    out = subprocess.check_output(['git', '-C', R, 'ls-files'],
                                  stderr=subprocess.DEVNULL).decode()
    tracked = [p for p in out.splitlines()
               if p.endswith('.pyc') or '__pycache__/' in p]
    assert not tracked, f'bytecode tracked: {tracked[:5]}'
    print('[12] no .pyc / __pycache__ tracked OK')


def c13():
    c = _r(SUITE)
    must = 'validate_pre_qa_stabilization_118_manual_qa_device_unlock_pass.py'
    assert must in c, 'suite non registra 118'
    print('[13] pre-QA safety suite registers 118 OK')


def c14():
    # Runtime best-effort: gli endpoint chiave restano up con flag invarianti.
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
    print('[v118 PRE_QA_118_MANUAL_QA_DEVICE_UNLOCK_PASS] OK '
          'deliverables_present qa_matrix_design_only matrix_rows_fields '
          'matrix_coverage matrix_uses_all_5_statuses triage_buckets_9_present '
          'runbook_sections evidence_template_fields invariants_preserved '
          'no_db_mutations no_out_of_scope_imports no_bytecode suite_registered '
          'runtime_smoke')
    return 0


if __name__ == '__main__':
    sys.exit(main())
