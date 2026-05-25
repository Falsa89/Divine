#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT — Track A validator.
# Audit-only: verifica consistenza canonica del findings dump.
import json, sys
from pathlib import Path

P = Path('/app/data/design/mobile_qa/project_player_facing_legacy_surfaces_findings_v1.json')


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_MOBILE_QA_AND_REPO_FINDINGS_CONSOLIDATION_READY'
    assert d['task_id'] == 'PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT'
    assert d['track'] == 'A'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    uqa = d['user_mobile_qa_findings']
    repo = d['repo_audit_findings']
    assert len(uqa) >= 8, 'expected at least 8 user QA findings'
    assert len(repo) >= 8, 'expected at least 8 repo audit findings'
    # Ogni finding ha id/area/observation/severity/classification
    for entry in uqa + repo:
        for k in ('id', 'observation', 'severity', 'classification'):
            assert k in entry, f'missing {k} in {entry}'
    allowed_sev = {'none', 'low', 'medium', 'high', 'critical'}
    for entry in uqa + repo:
        assert entry['severity'] in allowed_sev
    # Almeno un finding critical/high atteso
    assert any(e['severity'] in ('critical', 'high') for e in repo), 'expected at least one high/critical repo finding'
    print('[PASS] PLAYER-LEGACY Track A findings consolidation \u2014 {} user + {} repo'.format(len(uqa), len(repo)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
