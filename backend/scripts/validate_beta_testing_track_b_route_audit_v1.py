#!/usr/bin/env python3
# BETA_TESTING Track B — player route static audit script present, executable, and PASS=13.
import json, sys, subprocess
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_b_route_audit_v1.json')
SCRIPT = Path('/app/backend/scripts/run_player_route_static_audit.py')
REPORT = Path('/app/backend/reports/player_route_static_audit_latest.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_PLAYER_ROUTE_STATIC_AUDIT_SCRIPT_READY'
    assert SCRIPT.exists()
    # Run the audit fresh and capture the report
    rc = subprocess.run(['python3', str(SCRIPT)], capture_output=True, text=True, timeout=30)
    assert rc.returncode == 0, f'audit returned {rc.returncode}: {rc.stderr}'
    assert REPORT.exists(), 'audit report not written'
    rep = json.loads(REPORT.read_text())
    assert rep['routes_audited'] >= 12
    assert rep['fail'] == 0, f'audit FAIL count: {rep["fail"]} — routes failing: {[r["route"] for r in rep["results"] if r["verdict"]=="FAIL"]}'
    assert rep['miss'] == 0, f'audit MISS count: {rep["miss"]}'
    print(f'[PASS] BETA_TESTING Track B route audit: pass={rep["pass"]} warn={rep["warn"]} fail={rep["fail"]} miss={rep["miss"]}')
    return 0
if __name__ == '__main__': sys.exit(main())
