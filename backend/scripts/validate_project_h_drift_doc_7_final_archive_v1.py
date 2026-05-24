#!/usr/bin/env python3
"""PROJECT_H Track D validator — drift doc 7 FINAL archive."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_h_drift_doc_7_final_archive_v1.json')
PRIORS = [
    '/app/data/design/system_safety/project_b_drift_doc_1_legacy_summon_rate_archive_v1.json',
    '/app/data/design/system_safety/project_c_drift_doc_2_archive_v1.json',
    '/app/data/design/system_safety/project_d_drift_doc_3_archive_v1.json',
    '/app/data/design/system_safety/project_e_drift_doc_4_archive_v1.json',
    '/app/data/design/system_safety/project_f_drift_doc_5_archive_v1.json',
    '/app/data/design/system_safety/project_g_drift_doc_6_archive_v1.json',
]


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_D_DRIFT_DOC_7_FINAL_ARCHIVE_READY': fail('verdict mismatch')
    if m.get('archive_state') != 'KNOWN_NONBLOCKING_ARCHIVED_V1': fail('archive_state mismatch')
    if m.get('db_cleanup_executed') is not False: fail('db_cleanup_executed must be False')
    if m.get('db_cleanup_authorized') is not False: fail('db_cleanup_authorized must be False')
    if m.get('archived_docs_total') != '7/7': fail('archived_docs_total must be 7/7')
    if m.get('all_drift_categories_now_archived') is not True: fail('all_drift_categories_now_archived must be True')
    forb = m.get('forbidden_in_track_d_respected', {})
    for k in ('db_cleanup', 'gacha_summon_behavior_change', 'roster_mutation', 'borea_activation'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_d.{k} must be False')
    for p in PRIORS:
        if not Path(p).exists(): fail(f'prior drift archive missing: {p}')
    print('[PASS] PROJECT_H Track D drift doc 7 FINAL archive READY: 7/7 archived; all drift categories now archived; no DB cleanup')
    sys.exit(0)

if __name__ == '__main__': main()
