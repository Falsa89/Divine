#!/usr/bin/env python3
# BETA_TESTING Track A — baseline + branch policy lock.
import json, sys, hashlib, subprocess
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_a_baseline_v1.json')
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_A_BASELINE_AND_BRANCH_POLICY_LOCKED'
    # Branch policy minimum content
    bp = d['branch_policy']
    assert bp['working_branch_inside_container'] == 'master'
    assert 'support_agent' in bp['discrepancy_resolution'] or 'platform' in bp['discrepancy_resolution']
    assert 'md5 of in-container file via md5sum' in bp['truthful_proof_requirements_on_request']
    # Baseline invariants must match real files
    base = d['baseline_md5']
    assert md5('/app/backend/battle_engine.py') == base['backend/battle_engine.py']
    assert md5('/app/backend/.env') == base['backend/.env']
    assert md5('/app/frontend/app/soul-forge.tsx') == base['frontend/app/soul-forge.tsx']
    # Branch confirmed locally
    branch = subprocess.run(['git','-C','/app','rev-parse','--abbrev-ref','HEAD'],
                            capture_output=True, text=True).stdout.strip()
    assert branch == 'master', f'unexpected branch: {branch}'
    print('[PASS] BETA_TESTING Track A baseline + branch policy locked')
    return 0
if __name__ == '__main__': sys.exit(main())
