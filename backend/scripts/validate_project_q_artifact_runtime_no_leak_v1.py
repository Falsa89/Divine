#!/usr/bin/env python3
"""PROJECT_Q Track G validator — runtime no-leak + no equipment / divine weapon conflation.

Verifica:
- audited_source_files esistono e NON contengono forbidden markers
- audited_endpoints e' una lista non vuota
- endpoint_leaks == 0 e source_emission_leaks == 0
- no_equipment_semantics_in_schema == True
- no_divine_weapon_conflation_in_schema == True
- battle_engine.py e battle_core.py non importano artifact runtime module
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_runtime_no_leak_v1.json')
FORBIDDEN_TOKENS = ('artifact_equipped', 'hero_artifact_gear_slot', 'divine_weapon_artifact', 'artifact_bonus_active')
FORBIDDEN_RUNTIME_IMPORTS = ('from artifacts_runtime', 'import artifacts_runtime', 'artifact_live_bonus_apply')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_ARTIFACT_RUNTIME_NO_LEAK_AND_NO_EQUIPMENT_SEMANTICS_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if not (m.get('audited_endpoints') or []):
        fail('audited_endpoints empty')
    if int(m.get('endpoint_leaks', -1)) != 0:
        fail('endpoint_leaks must be 0')
    if int(m.get('source_emission_leaks', -1)) != 0:
        fail('source_emission_leaks must be 0')
    if m.get('no_equipment_semantics_in_schema') is not True:
        fail('no_equipment_semantics_in_schema must be True')
    if m.get('no_divine_weapon_conflation_in_schema') is not True:
        fail('no_divine_weapon_conflation_in_schema must be True')
    # Independent file scan of audited source files
    audited = m.get('audited_source_files') or []
    if not audited:
        fail('audited_source_files empty')
    for src_path in audited:
        p = Path(src_path)
        if not p.exists():
            fail(f'audited source file missing: {src_path}')
        txt = p.read_text()
        for tok in FORBIDDEN_TOKENS:
            if tok in txt:
                fail(f'forbidden artifact runtime token "{tok}" found in {src_path}')
        for tok in FORBIDDEN_RUNTIME_IMPORTS:
            if tok in txt:
                fail(f'forbidden artifact runtime import "{tok}" found in {src_path}')
    print(f'[PASS] PROJECT_Q Track G runtime no-leak READY — 0 endpoint leaks, 0 source emission leaks, no equipment / divine weapon conflation')
    sys.exit(0)


if __name__ == '__main__':
    main()
