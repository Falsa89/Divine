#!/usr/bin/env python3
"""
PROJECT_NO_STAMINA_REMEDIATION validator (statico, surgical-patch verification).

Verifica che il pack abbia rimosso le vere violazioni stamina runtime e che
nessun riferimento canonico-vietato resti attivo nelle route gated/UI visibili.

Asserisce:
  - 4 JSON design/audit (A, B, C, D) + 1 proof marker
  - tutti i JSON syntactically validi + verdict atteso per track
  - 6 backend route patch applicati (combat.py x3, cosmetics.py, gvg.py, raids.py)
    -> nessun `if user.get("stamina"` pattern di gating in queste 4 file
    -> nessun `"$inc": {"stamina":` pattern di decremento in queste 4 file
  - 4 frontend label/badge patch applicati (events.tsx, gvg.tsx, shop.tsx, menu.tsx)
    -> stringa "Stamina" come label utente RIMOSSA da events.tsx, gvg.tsx, shop.tsx CATS, menu.tsx badge
  - PROJECT_NO_STAMINA_REMEDIATION audit-trail comment presente nei 10 patchati
  - Frontend locks ancora intatti (SHOP/BP/VIP/ITEM_SHOP_LOCKED_V2 = true)
  - MD5 invarianti baseline rispettati su battle_engine.py / .env /
    routes/artifacts.py / battlepass.tsx / vip.tsx
  - Soul Forge file NON toccato in questo pack
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/no_stamina'

REQUIRED_TRACKS = {
    'stamina_surface_audit_v1.json':                       'TRACK_A_STAMINA_SURFACE_AUDIT_READY',
    'controlled_remediation_patch_v1.json':                'TRACK_B_CONTROLLED_REMEDIATION_PATCH_READY',
    'mode_reachability_and_smoke_v1.json':                 'TRACK_C_MODE_REACHABILITY_AND_SMOKE_READY',
    'canonical_policy_and_future_entry_model_v1.json':     'TRACK_D_CANONICAL_POLICY_AND_FUTURE_ENTRY_MODEL_READY',
}
PROOF_MARKER = 'no_stamina_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py':       '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                   'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':    '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':    '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':           '45fcc9890b6b128c37088bc33aa54caf',
}

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
]

PATCHED_BACKEND = [
    'backend/routes/combat.py',
    'backend/routes/cosmetics.py',
    'backend/routes/gvg.py',
    'backend/routes/raids.py',
]
PATCHED_FRONTEND = [
    'frontend/app/events.tsx',
    'frontend/app/gvg.tsx',
    'frontend/app/shop.tsx',
    'frontend/app/(tabs)/menu.tsx',
]

# Patterns we expect to be GONE from patched files
FORBIDDEN_BACKEND_GATE_PATTERNS = [
    re.compile(r'if\s+user\.get\(\s*[\'"]stamina[\'"]'),
    re.compile(r'\$inc[\'"]?\s*:\s*\{\s*[\'"]stamina[\'"]\s*:\s*-'),
    re.compile(r'Stamina insufficiente'),
]

FORBIDDEN_FRONTEND_LABEL_PATTERNS = {
    'frontend/app/events.tsx':       [re.compile(r'\{ev\.stamina_cost\}')],
    'frontend/app/gvg.tsx':          [re.compile(r'12 stamina per attacco')],
    'frontend/app/shop.tsx':         [re.compile(r"\{id:'stamina',label:'Stamina'\}")],
    'frontend/app/(tabs)/menu.tsx':  [re.compile(r'value=\{`\$\{user\?\.stamina')],
}

AUDIT_TRAIL_TOKEN = 'PROJECT_NO_STAMINA_REMEDIATION'


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSON files present + valid + expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_NO_STAMINA_REMEDIATION':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) Proof marker
    pm = DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')

    # 3) MD5 invariants
    for rel, expected_hash in EXPECTED_INVARIANTS.items():
        actual = md5(ROOT / rel)
        if actual != expected_hash:
            fail(f'invariant drift on {rel}: expected {expected_hash} got {actual}')

    # 4) Frontend locks still in place
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 5) Backend route patched files: forbidden gate patterns REMOVED + audit-trail comment present
    for rel in PATCHED_BACKEND:
        content = (ROOT / rel).read_text(encoding='utf-8')
        if AUDIT_TRAIL_TOKEN not in content:
            fail(f'audit-trail comment {AUDIT_TRAIL_TOKEN!r} missing in {rel}')
        for pat in FORBIDDEN_BACKEND_GATE_PATTERNS:
            m = pat.search(content)
            if m:
                fail(f'forbidden stamina gate pattern still present in {rel}: {m.group(0)!r}')

    # 6) Frontend patched files: forbidden label patterns REMOVED + audit-trail comment present
    for rel in PATCHED_FRONTEND:
        content = (ROOT / rel).read_text(encoding='utf-8')
        if AUDIT_TRAIL_TOKEN not in content:
            fail(f'audit-trail comment {AUDIT_TRAIL_TOKEN!r} missing in {rel}')
        for pat in FORBIDDEN_FRONTEND_LABEL_PATTERNS.get(rel, []):
            m = pat.search(content)
            if m:
                fail(f'forbidden stamina label pattern still present in {rel}: {m.group(0)!r}')

    # 7) Soul Forge files NOT touched (Soul Forge protected)
    sf_be = (ROOT / 'backend/routes/soul_forge.py').read_text(encoding='utf-8')
    if AUDIT_TRAIL_TOKEN in sf_be:
        fail('Soul Forge backend MUST NOT be touched in this pack')
    sf_fe = (ROOT / 'frontend/app/soul-forge.tsx').read_text(encoding='utf-8')
    if AUDIT_TRAIL_TOKEN in sf_fe:
        fail('Soul Forge frontend MUST NOT be touched in this pack')

    # 8) battle_engine.py NOT touched (already covered by MD5; double-check no audit token)
    be = (ROOT / 'backend/battle_engine.py').read_text(encoding='utf-8')
    if AUDIT_TRAIL_TOKEN in be:
        fail('battle_engine.py MUST NOT be touched in this pack')
    # combat.tsx no broad refactor (no audit-trail token - it must not contain remediation comments)
    cf = (ROOT / 'frontend/app/combat.tsx').read_text(encoding='utf-8')
    if AUDIT_TRAIL_TOKEN in cf:
        fail('frontend/app/combat.tsx MUST NOT be broadly refactored in this pack')

    # 9) Track A: db_writes 0 + 6 backend + 4 frontend true violations
    a = json.loads((DIR / 'stamina_surface_audit_v1.json').read_text())
    if a.get('audit_only') is not True:
        fail('Track A audit_only must be True')
    if a.get('db_writes') != 0:
        fail('Track A db_writes must be 0')
    if a.get('canonical_decision') != 'NO_STAMINA_SYSTEM':
        fail('Track A canonical_decision must be NO_STAMINA_SYSTEM')
    cnt = a.get('counts', {})
    if cnt.get('true_violations_backend') != 6:
        fail(f'Track A true_violations_backend must be 6; got {cnt.get("true_violations_backend")}')
    if cnt.get('true_violations_frontend') != 4:
        fail(f'Track A true_violations_frontend must be 4; got {cnt.get("true_violations_frontend")}')
    if cnt.get('patches_applied') != 10:
        fail(f'Track A patches_applied must be 10; got {cnt.get("patches_applied")}')

    # 10) Track B: 10 patches + zero DB writes via script + new economy NOT introduced
    b = json.loads((DIR / 'controlled_remediation_patch_v1.json').read_text())
    if b.get('db_writes_via_script') != 0:
        fail('Track B db_writes_via_script must be 0')
    if b.get('db_migrations') != 0:
        fail('Track B db_migrations must be 0')
    if b.get('wallet_balance_changes') is not False:
        fail('Track B wallet_balance_changes must be False')
    if b.get('new_economy_introduced') is not False:
        fail('Track B new_economy_introduced must be False')
    if b.get('premium_stamina_refill_introduced') is not False:
        fail('Track B premium_stamina_refill_introduced must be False')
    patches = b.get('patches', [])
    if len(patches) != 10:
        fail(f'Track B must have exactly 10 patches; got {len(patches)}')
    bcounts = b.get('counts', {})
    if bcounts.get('protected_files_touched') != 0:
        fail(f'Track B protected_files_touched must be 0; got {bcounts.get("protected_files_touched")}')

    # 11) Track C: all 6 pre-blocked modes now reachable
    c = json.loads((DIR / 'mode_reachability_and_smoke_v1.json').read_text())
    if c.get('static_check_only') is not True:
        fail('Track C static_check_only must be True')
    locks = c.get('frontend_lock_invariants_post_patch', {})
    for key in ['VIP_LOCKED_V2 = true', 'BP_LOCKED_V2 = true', 'BP_PREMIUM_BUY_LOCKED_V2 = true',
                'SHOP_LOCKED_V2 = true', 'ITEM_SHOP_LOCKED_V2 = true']:
        if locks.get(key) is not True:
            fail(f'Track C lock invariant {key} must be True')
    ccnt = c.get('counts', {})
    if ccnt.get('modes_blocked_pre_patch') != 6:
        fail(f'Track C modes_blocked_pre_patch must be 6; got {ccnt.get("modes_blocked_pre_patch")}')
    if ccnt.get('modes_reachable_post_patch') != 10:
        fail(f'Track C modes_reachable_post_patch must be 10; got {ccnt.get("modes_reachable_post_patch")}')

    # 12) Track D: no new economy + forbidden_constructs lists premium_stamina_refill_iap
    d = json.loads((DIR / 'canonical_policy_and_future_entry_model_v1.json').read_text())
    if d.get('db_writes') != 0:
        fail('Track D db_writes must be 0')
    if d.get('design_only') is not True:
        fail('Track D design_only must be True')
    policy = d.get('canonical_policy_no_stamina_v1', {})
    forbidden = policy.get('forbidden_constructs', [])
    must_have_forbidden = {
        'global_stamina_wallet', 'premium_stamina_refill_iap',
        'stamina_cost_to_play_mode', 'vip_stamina_max_perk',
        'battle_pass_stamina_reward_active_grant', 'shop_category_stamina_visible',
    }
    if not must_have_forbidden.issubset(set(forbidden)):
        fail(f'Track D forbidden_constructs missing: {sorted(must_have_forbidden - set(forbidden))}')
    allowed = policy.get('allowed_constructs', [])
    if not any('guild_attack_attempts' in a for a in allowed):
        fail('Track D allowed_constructs must include guild_attack_attempts')
    if not any('mode_attempts' in a for a in allowed):
        fail('Track D allowed_constructs must include mode_attempts')

    print('[PASS] PROJECT_NO_STAMINA_REMEDIATION master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
