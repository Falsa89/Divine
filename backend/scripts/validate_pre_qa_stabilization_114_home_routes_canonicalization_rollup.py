#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — ROLLUP.

Pack 115F repair:
- Il rollup precedente verificava solo l'esistenza dei file (rischio di
  false-confidence: lo script poteva "passare" anche se il validator/smoke
  erano rotti).
- Ora il rollup ESEGUE effettivamente validator e smoke come subprocess e
  fallisce (returncode != 0) se uno dei due fallisce.
- Mantiene il check di esistenza del report finale 116 (esistenza file
  necessaria ma NON sufficiente).
"""
import os
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

REQUIRED_SCRIPTS = (
    'validate_pre_qa_stabilization_114_home_routes_canonicalization.py',
    'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py',
)

REQUIRED_REPORT = 'docs/divine/116_PRE_QA_STABILIZATION_114_HOME_ROUTES_CANONICALIZATION_FINAL_REPORT.md'


def _run_child(name: str) -> None:
    fp = os.path.join(SCRIPTS, name)
    assert os.path.exists(fp), f'manca lo script figlio: {name}'
    # check_call solleva CalledProcessError se returncode != 0 → fail forte.
    subprocess.check_call([sys.executable, fp])
    print(f'  [ROLLUP-CHILD-OK] {name}')


# 1) Esistenza file figli (necessaria ma non sufficiente).
for s in REQUIRED_SCRIPTS:
    assert os.path.exists(os.path.join(SCRIPTS, s)), s

# 2) Esistenza report finale (necessaria ma non sufficiente).
assert os.path.exists(os.path.join(R, REQUIRED_REPORT)), (
    f'report finale 116 mancante: {REQUIRED_REPORT}'
)

# 3) Esecuzione effettiva di validator e smoke (necessaria per PASS).
for s in REQUIRED_SCRIPTS:
    _run_child(s)

print('[PRE_QA_STABILIZATION_114_ROLLUP] OK validator_executed smoke_executed report_present')
