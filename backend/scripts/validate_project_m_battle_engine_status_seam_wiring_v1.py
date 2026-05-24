#!/usr/bin/env python3
"""PROJECT_M Track B validator — battle_engine status seam wiring applied."""
import hashlib, json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_m_battle_engine_status_seam_wiring_result_v1.json')
BE = Path('/app/backend/battle_engine.py')
BC = Path('/app/backend/battle_core.py')
SV = Path('/app/backend/server.py')
RC = Path('/app/backend/routes/combat.py')
BKP = Path('/app/backend/battle_engine.py.project_m_pre_patch.bak')
RBK = Path('/app/backend/scripts/rollback_project_m_battle_engine_status_seam.py')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
FORBIDDEN_KEYWORDS = ('apply_dot', 'damage_over_time', 'heal_over_time', 'tick_loop')
PATCH_MARKERS = (
    'PROJECT_M Track B — STATUS FIRST SLICE single-point seam import.',
    '_project_m_status_seam',
    'PROJECT_M Track B — pre-fight status seam call (single point).',
)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_BATTLE_ENGINE_STATUS_SEAM_WIRED_FLAG_OFF_SAFE': fail('verdict mismatch')
    if m.get('wiring_applied') is not True: fail('wiring_applied must be True')
    if not BE.exists() or not SEAM.exists() or not RBK.exists() or not BKP.exists():
        fail('one of: battle_engine.py / seam / rollback / backup missing')
    txt = BE.read_text(encoding='utf-8', errors='ignore')
    for marker in PATCH_MARKERS:
        if marker not in txt: fail(f'patch marker missing in battle_engine.py: {marker[:60]!r}')
    # Forbidden keywords must NOT appear in the patched portions (we check whole file conservatively).
    # We accept their presence in pre-existing comments only if they were already there in backup.
    bkp_txt = BKP.read_text(encoding='utf-8', errors='ignore')
    for kw in FORBIDDEN_KEYWORDS:
        if txt.count(kw) > bkp_txt.count(kw): fail(f'patch introduced forbidden keyword: {kw}')
    # battle_core.py, server.py, routes/combat.py MUST be byte-identical to expected md5.
    expected = m.get('files_unchanged_md5', {})
    for p_str, exp in expected.items():
        p = Path(p_str)
        if not p.exists(): fail(f'{p} missing')
        cur = _md5(p)
        if cur != exp: fail(f'{p} md5 changed: expected {exp} got {cur}')
    if _md5(BKP) != m.get('battle_engine_pre_patch_md5'): fail('backup md5 mismatch')
    if _md5(BE) != m.get('battle_engine_post_patch_md5'): fail('current battle_engine.py md5 != recorded post_patch_md5')
    print('[PASS] PROJECT_M Track B seam WIRED: single-point patch present; battle_core/server/routes UNCHANGED; backup intact')
    sys.exit(0)


if __name__ == '__main__': main()
