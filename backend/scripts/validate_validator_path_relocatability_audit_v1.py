#!/usr/bin/env python3
"""PRE_QA_P0 — validate_validator_path_relocatability_audit_v1.

Audit statico read-only di TUTTI i validator in backend/scripts/validate_*.py
per individuare quelli con path assoluti '/app/...' hardcoded.

Distingue:
  - validator_relocatable (no '/app/' literal nei path)
  - validator_hardcoded_app_path (almeno una stringa literal "/app/...")
  - current_validators (i nostri current-state truth source, gia' relocatable)

NON dichiara fittiziamente che tutti i validator sono relocatable: produce
elenco onesto + remediation plan.

Output JSON in backend/reports/validator_path_relocatability_audit_latest.json.

Exit code:
  - 0 sempre (l'audit e' diagnostic; il fail bloccante e' demandato a chi
    decidera' di rifattorizzare). FAIL solo se incoerenza di setup.

NOTA: hardcoded /app non e' di per se' un bug runtime nel container ufficiale
dove R == '/app'; e' un bug di portabilita'/relocatability. Il P0 lo registra.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
SCRIPTS_DIR = os.path.join(R, 'backend', 'scripts')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Sorgenti di verita' (questi validator sono i nostri current-state truth).
CURRENT_STATE_TRUTH_VALIDATORS = {
    'validate_pre_qa_pack_119c_menu_public_snapshot.py',
    'validate_pre_qa_pack_119d_public_menu_route_health.py',
    'validate_pre_qa_pack_120a_controlled_unlock_prep.py',
    'validate_pre_qa_acceleration_120b_safe_playable_vertical_slice_combo.py',
    'validate_v89_home_battle_flow_audit.py',
    'validate_v89_no_asset_final_import_no_character_bible.py',
    'validate_v89_real_battlefield_tsx.py',
    'validate_mega_release_acceleration_38_v89_rollup.py',
    'validate_current_zip_truth_rebaseline_v1.py',
    'validate_validator_path_relocatability_audit_v1.py',
    'validate_stale_md5_supersedence_audit_v1.py',
    'validate_current_public_guardrail_snapshot_v1.py',
}

# Regex: literal "/app/..." come stringa quotata. Escludiamo i commenti.
_APP_LITERAL_RE = re.compile(r"['\"]\/app\/")
_LINE_COMMENT_RE = re.compile(r'#.*$', re.MULTILINE)
# Triple-quoted docstring (semplice ma sufficiente per file ben formati).
_TRIPLE_STR_RE = re.compile(r'(?s)("""|\'\'\').*?\1')


def _strip_py_comments(src: str) -> str:
    # Rudimentale: rimuove commenti # ma preserva stringhe normali. Inoltre
    # rimuoviamo docstring triple-quoted: contengono spesso esempi/literal
    # come '/app/...' che NON sono path runtime ma documentazione.
    s = _TRIPLE_STR_RE.sub('', src)
    s = _LINE_COMMENT_RE.sub('', s)
    return s


def _scan_file(fp: str) -> dict:
    try:
        src = open(fp, encoding='utf-8', errors='replace').read()
    except Exception as e:
        return {'error': f'{type(e).__name__}: {e}'}
    code = _strip_py_comments(src)
    in_code = len(_APP_LITERAL_RE.findall(code))
    total = len(_APP_LITERAL_RE.findall(src))
    return {'in_code': in_code, 'total_incl_comments': total}


def main() -> int:
    if not os.path.isdir(SCRIPTS_DIR):
        print(f'FAIL: scripts dir mancante: {SCRIPTS_DIR}')
        return 1

    all_validators = sorted(
        f for f in os.listdir(SCRIPTS_DIR)
        if f.startswith('validate_') and f.endswith('.py')
    )

    relocatable = []
    hardcoded = []
    parse_errors = []
    current_state_truth = []

    for v in all_validators:
        fp = os.path.join(SCRIPTS_DIR, v)
        scan = _scan_file(fp)
        if 'error' in scan:
            parse_errors.append({'validator': v, 'error': scan['error']})
            continue
        is_current = v in CURRENT_STATE_TRUTH_VALIDATORS
        rec = {
            'validator': v,
            'app_literal_in_code': scan['in_code'],
            'app_literal_total': scan['total_incl_comments'],
            'is_current_state_truth': is_current,
        }
        if scan['in_code'] > 0:
            hardcoded.append(rec)
        else:
            relocatable.append(rec)
        if is_current:
            current_state_truth.append(rec)

    # Sanity: tutti i nostri current_state_truth validators DEVONO essere
    # relocatable (no '/app/' literal nel codice eseguibile).
    truth_with_app_literal = [
        r for r in current_state_truth if r['app_literal_in_code'] > 0
    ]

    failures = []
    if parse_errors:
        for pe in parse_errors:
            failures.append(f'parse error: {pe}')
    if truth_with_app_literal:
        # E' un fail bloccante: i nostri truth validators non possono avere
        # path assoluti hardcoded.
        for r in truth_with_app_literal:
            failures.append(
                f"CURRENT-STATE-TRUTH validator with hardcoded /app/: "
                f"{r['validator']} (count={r['app_literal_in_code']})")

    report = {
        'tool': 'validate_validator_path_relocatability_audit_v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'scripts_dir': os.path.relpath(SCRIPTS_DIR, R),
        'totals': {
            'all_validators': len(all_validators),
            'relocatable': len(relocatable),
            'hardcoded_app_path': len(hardcoded),
            'parse_errors': len(parse_errors),
            'current_state_truth_total': len(current_state_truth),
            'current_state_truth_with_hardcoded_app_literal': len(truth_with_app_literal),
        },
        'current_state_truth_validators': sorted(CURRENT_STATE_TRUTH_VALIDATORS),
        'current_state_truth_details': current_state_truth,
        'hardcoded_sample_first_30': hardcoded[:30],
        'parse_errors': parse_errors,
        'remediation_plan': {
            'recommended_pattern': "use os.path.dirname(...) chain instead of an absolute root-level literal path",
            'priority_targets': [
                'validator legacy con stale baseline (validate_beta_testing_*_v1.py, validate_project_full_runtime_feature_reality_audit_v1.py)',
                'mega_release_acceleration_* legacy non-corrispondenti al current ZIP',
            ],
            'do_not_break_required_validator_contract': True,
            'do_not_fake_pass': True,
        },
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }

    out_fp = os.path.join(
        REPORTS_DIR, 'validator_path_relocatability_audit_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('============== VALIDATOR PATH RELOCATABILITY AUDIT ==============')
    print(f"  total validators:                 {report['totals']['all_validators']}")
    print(f"  relocatable (no /app literal in code): {report['totals']['relocatable']}")
    print(f"  hardcoded /app literal in code:        {report['totals']['hardcoded_app_path']}")
    print(f"  current-state-truth validators:        {report['totals']['current_state_truth_total']}")
    print(f"  truth with hardcoded /app literal:     {report['totals']['current_state_truth_with_hardcoded_app_literal']}")
    print(f"  parse errors:                          {report['totals']['parse_errors']}")
    print(f"  verdict: {report['verdict']}")
    print(f"  JSON:    {out_fp}")
    print('=================================================================')

    if failures:
        print('')
        print('[v_p0_relocatability_audit] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1

    print('')
    print('[v_p0_relocatability_audit] OK '
          f"current_state_truth_clean=True "
          f"hardcoded_count={report['totals']['hardcoded_app_path']} "
          f"relocatable_count={report['totals']['relocatable']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
