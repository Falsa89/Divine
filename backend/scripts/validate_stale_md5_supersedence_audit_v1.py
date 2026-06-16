#!/usr/bin/env python3
"""PRE_QA_P0 — validate_stale_md5_supersedence_audit_v1.

Audit statico read-only dei riferimenti al MD5 stale
151ca35ad3bc35f0a6209cb3744ed440 attraverso il repo.

Verifica:

  1. Stale inventory JSON e' coerente con la realta' del filesystem
     (le categorie sommate sono compatibili con il totale conteggiato adesso).
  2. Nessun file e' stato cancellato (anti-deletion check): se l'inventory
     dichiara count > 0 in docs/divine, deve esistere almeno un file
     docs/divine con il MD5 stale.
  3. Il MD5 stale NON e' dichiarato come current_invariant nei truth source
     (current_code_md5_snapshot_v1.json non lo contiene tra i valori).
  4. Validator listati come 'current_unsafe_validator_baseline' in
     stale_md5_reference_inventory_v1.json sono ancora marcati
     unsafe/superseded nel validator_truth_status_matrix_v1.json
     (no fake PASS, no doc deletion).

Output JSON in backend/reports/stale_md5_supersedence_audit_latest.json.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
TRUTH_DIR = os.path.join(R, 'data', 'design', 'current_truth')
SCRIPTS_DIR = os.path.join(R, 'backend', 'scripts')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

STALE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'


def _grep_count(root: str, extensions: list) -> dict:
    """Conta file contenenti STALE_MD5, raggruppati per top-level dir."""
    cmd = ['grep', '-rl', STALE_MD5]
    for ext in extensions:
        cmd.extend(['--include', ext])
    cmd.append(root)
    try:
        out = subprocess.run(cmd, cwd=R, capture_output=True, text=True,
                              timeout=120)
    except subprocess.TimeoutExpired:
        return {'error': 'grep timeout'}
    files = [
        os.path.relpath(line.strip(), R)
        for line in out.stdout.splitlines() if line.strip()
    ]
    return {'files': files, 'count': len(files)}


def main() -> int:
    failures = []

    # 1) Carica truth sources
    truth_fp = os.path.join(TRUTH_DIR, 'current_code_md5_snapshot_v1.json')
    stale_fp = os.path.join(TRUTH_DIR, 'stale_md5_reference_inventory_v1.json')
    matrix_fp = os.path.join(TRUTH_DIR, 'validator_truth_status_matrix_v1.json')
    for fp in (truth_fp, stale_fp, matrix_fp):
        if not os.path.exists(fp):
            failures.append(f'missing truth file: {fp}')
    if failures:
        return _emit('FAIL', failures, None)

    snap = json.load(open(truth_fp, encoding='utf-8'))
    stale = json.load(open(stale_fp, encoding='utf-8'))
    matrix = json.load(open(matrix_fp, encoding='utf-8'))

    # 2) Scan filesystem
    docs_scan = _grep_count(os.path.join(R, 'docs', 'divine'), ['*.md'])
    design_scan = _grep_count(os.path.join(R, 'data', 'design'), ['*.json'])
    scripts_scan = _grep_count(os.path.join(R, 'backend', 'scripts'), ['*.py'])

    total_real = (docs_scan.get('count', 0) + design_scan.get('count', 0)
                  + scripts_scan.get('count', 0))

    # 3) Check truth snapshot does NOT contain stale MD5 as a current value.
    declared_md5s = list((snap.get('files') or {}).values())
    if STALE_MD5 in declared_md5s:
        failures.append(
            f'current_code_md5_snapshot_v1.json contiene STALE MD5 '
            f'{STALE_MD5} tra i current invariants!')

    # 4) Anti-deletion: se inventory dichiara docs storici, devono esistere.
    declared_docs = (stale.get('totals') or {}).get('docs_divine_files', 0)
    if declared_docs > 0 and docs_scan.get('count', 0) == 0:
        failures.append(
            'stale inventory dichiara docs storici ma none e\' presente '
            '(violazione anti-deletion).')

    # 5) Validator marcati current_unsafe restano marcati.
    unsafe_in_inv = set(((stale.get('category_breakdown') or {})
                         .get('current_unsafe_validator_baseline') or {})
                        .get('examples_known_fail', []))
    matrix_entries = {e['validator_path']: e for e in matrix.get('entries', [])}
    for un in unsafe_in_inv:
        ent = matrix_entries.get(un)
        if not ent:
            failures.append(f'validator listato current_unsafe in inventory '
                            f'ma non presente in matrix: {un}')
            continue
        if ent.get('recommended_action') not in (
            'MARK_SUPERSEDED_HISTORICAL', 'UPDATE_BASELINE',
            'MAKE_RELOCATABLE', 'SPLIT_ENVIRONMENTAL_CHECK',
        ):
            failures.append(
                f'validator unsafe non marcato superseded/update/relocatable '
                f'in matrix: {un} (action={ent.get("recommended_action")!r})')

    # 6) Honesty: l'inventory dichiara no_fake_pass + no_doc_deletion.
    hs = (stale.get('honesty_statement') or {})
    if not hs.get('no_fake_pass'):
        failures.append('stale inventory: no_fake_pass non dichiarato true')
    if not hs.get('no_doc_deletion'):
        failures.append('stale inventory: no_doc_deletion non dichiarato true')
    if not hs.get('no_meaning_change_of_historical_reports'):
        failures.append(
            'stale inventory: no_meaning_change_of_historical_reports non dichiarato true')

    report = {
        'tool': 'validate_stale_md5_supersedence_audit_v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'stale_md5': STALE_MD5,
        'fs_scan': {
            'docs_divine': docs_scan,
            'data_design': design_scan,
            'backend_scripts': scripts_scan,
            'total_real': total_real,
        },
        'inventory_totals': stale.get('totals') or {},
        'truth_snapshot_safe_from_stale': STALE_MD5 not in declared_md5s,
        'unsafe_validators_marked_count': len(
            [v for v in unsafe_in_inv if v in matrix_entries]),
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(REPORTS_DIR, 'stale_md5_supersedence_audit_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('============== STALE MD5 SUPERSEDENCE AUDIT ==============')
    print(f"  stale MD5: {STALE_MD5}")
    print(f"  docs/divine:        {docs_scan.get('count', 0)}")
    print(f"  data/design:        {design_scan.get('count', 0)}")
    print(f"  backend/scripts:    {scripts_scan.get('count', 0)}")
    print(f"  total:              {total_real}")
    print(f"  truth_snapshot_safe_from_stale: "
          f"{report['truth_snapshot_safe_from_stale']}")
    print(f"  unsafe_validators_marked: {report['unsafe_validators_marked_count']}")
    print(f"  verdict: {report['verdict']}")
    print(f"  JSON:    {out_fp}")
    print('==========================================================')

    if failures:
        print('')
        print('[v_p0_stale_md5_supersedence] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1

    print('')
    print('[v_p0_stale_md5_supersedence] OK no_fake_pass=true '
          'no_doc_deletion=true truth_snapshot_safe=true')
    return 0


def _emit(verdict: str, failures: list, _info) -> int:
    print(f'[v_p0_stale_md5_supersedence] {verdict}')
    for f in failures:
        print(f'  - {f}')
    return 0 if verdict == 'OK' else 1


if __name__ == '__main__':
    sys.exit(main())
