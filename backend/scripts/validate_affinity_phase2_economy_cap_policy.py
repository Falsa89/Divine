#!/usr/bin/env python3
"""
AF2-B — Validator for affinity_phase2_economy_cap_policy_draft_v1.json

Verifies:
  - policy file present and parses as JSON
  - policy_id and task_origin correct
  - design_only=true, runtime_attached=false, db_write=false, no_borea_activation=true
  - stat_buff_live=false on every affinity tier
  - PvP cap per source <= 2 and total <= 6
  - Borea-locked across all gift value tiers and affinity tiers
  - no adult/explicit naming
  - no paid-only mandatory progression
  - source_catalog (AF2-A gift draft) exists and is referenced
  - no endpoint created and no UI button created (grep)

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
POLICY_PATH = ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_economy_cap_policy_draft_v1.json'
GIFT_DRAFT_PATH = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
BACKEND_ROUTES_DIR = ROOT / 'backend' / 'routes'
FRONTEND_APP_DIR = ROOT / 'frontend' / 'app'

ENDPOINT_PATTERNS = [
    r'/api/affinity/gift-?spend',
    r'/api/affinity/gift_spend',
    r'/api/affinity/spend',
]
UI_BUTTON_PATTERNS = [
    r'"Gift\s*Spend"', r"'Gift\s*Spend'",
    r'"GiftSpendButton"', r"'GiftSpendButton'",
    r'gift[_-]?spend[_-]?button',
]
# Adult/explicit blacklist. We exclude documentation tokens that *forbid* adult content
# (e.g. `no_adult_or_explicit_gifts`, `adult_explicit_naming_forbidden`). The intent
# is to flag positive uses such as actual NSFW gift/skin entries.
ADULT_BLACKLIST = ['nsfw', 'lewd', 'erotic', 'porn', 'xxx', 'explicit_sex']
ADULT_CONTEXT_REGEX = re.compile(
    r'(?<![a-z_])adult(?![a-z_]*(?:_explicit_naming_forbidden|_blacklist))',
    re.IGNORECASE,
)
ADULT_NEGATIVE_PREFIXES = ('no_adult', 'adult_explicit_naming_forbidden',
                           'no_adult_or_explicit_gifts')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Policy file
record('policy_file_present', POLICY_PATH.exists(), str(POLICY_PATH))
try:
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    record('policy_file_parses', True, '')
except Exception as e:
    record('policy_file_parses', False, f'{e!r}')
    policy = {}

# 2. Identity
record('policy_id', policy.get('policy_id') == 'affinity_phase2_economy_cap_policy_draft_v1',
       f'got {policy.get("policy_id")}')
record('task_origin', policy.get('task_origin') == 'AF2-B',
       f'got {policy.get("task_origin")}')
record('baseline_anchor',
       policy.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm132c2_v5',
       f'got {policy.get("baseline_anchor")}')

# 3. Safety flags
for key, expected in [
    ('design_only', True),
    ('runtime_attached', False),
    ('battle_runtime_attached', False),
    ('applied_to_combat', False),
    ('db_write', False),
    ('no_borea_activation', True),
    ('no_runtime_feature_flag_on', True),
]:
    record(f'top_level_{key}', policy.get(key) == expected,
           f'expected {expected}, got {policy.get(key)!r}')

sf = policy.get('safety_flags') or {}
for key, expected in [
    ('runtime_attached', False),
    ('applied_to_combat', False),
    ('db_write', False),
    ('borea_activation_allowed', False),
    ('stat_buff_live', False),
    ('adult_explicit_naming', False),
    ('paid_only_mandatory_progression', False),
    ('feature_flag_currently_enabled', False),
]:
    record(f'safety_flags_{key}', sf.get(key) == expected,
           f'expected {expected}, got {sf.get(key)!r}')

# 4. Cap policy
cp = policy.get('cap_policy') or {}
record('cap_policy_no_combat_stat_buff_initially',
       cp.get('no_combat_stat_buff_initially') is True, '')
record('cap_policy_pvp_per_source_le_2',
       isinstance(cp.get('pvp_cap_per_source_pct'), (int, float))
       and cp.get('pvp_cap_per_source_pct') <= 2,
       f'got {cp.get("pvp_cap_per_source_pct")}')
record('cap_policy_pvp_total_le_6',
       isinstance(cp.get('pvp_cap_total_pct'), (int, float))
       and cp.get('pvp_cap_total_pct') <= 6,
       f'got {cp.get("pvp_cap_total_pct")}')
record('cap_policy_borea_locked',
       cp.get('borea_gifts_locked_until_visible_active') is True, '')
record('cap_policy_no_adult', cp.get('no_adult_or_explicit_gifts') is True, '')
record('cap_policy_no_paid_only',
       cp.get('no_paid_only_mandatory_progression') is True, '')

# 5. Gift value tiers
gvts = policy.get('gift_value_tiers') or []
required_tier_ids = {
    'universal_small', 'faction_favored', 'element_favored',
    'faction_element_favored', 'event_limited_future',
}
got_tier_ids = {t.get('id') for t in gvts if isinstance(t, dict)}
record('gift_value_tiers_present', required_tier_ids.issubset(got_tier_ids),
       f'missing: {required_tier_ids - got_tier_ids}')
for t in gvts:
    if not isinstance(t, dict):
        continue
    tid = t.get('id')
    record(f'gift_value_tier_borea_locked:{tid}', t.get('borea_locked') is True, '')
    record(f'gift_value_tier_adult_forbidden:{tid}',
           t.get('adult_explicit_naming_forbidden') is True, '')

# 6. Affinity tiers
ats = policy.get('affinity_tiers') or []
required_tiers = {'tier_0', 'tier_1', 'tier_2', 'tier_3', 'tier_4'}
got_tiers = {t.get('id') for t in ats if isinstance(t, dict)}
record('affinity_tiers_present', required_tiers.issubset(got_tiers),
       f'missing: {required_tiers - got_tiers}')
labels = {t.get('id'): t.get('label') for t in ats if isinstance(t, dict)}
expected_labels = {
    'tier_0': 'acquaintance', 'tier_1': 'trusted', 'tier_2': 'bonded',
    'tier_3': 'devoted', 'tier_4': 'oathbound_future',
}
for k, v in expected_labels.items():
    record(f'affinity_tier_label:{k}', labels.get(k) == v,
           f'expected {v}, got {labels.get(k)}')
for t in ats:
    if not isinstance(t, dict):
        continue
    tid = t.get('id')
    record(f'affinity_tier_stat_buff_live_false:{tid}',
           t.get('stat_buff_live') is False, '')
    record(f'affinity_tier_borea_locked:{tid}',
           t.get('borea_locked') is True, '')

# 7. No endpoint created (grep backend/routes)
# Exclude affinity_gift_spend.py (AF2-G disabled skeleton; explicitly
# authorized future-ready endpoint that returns 423 and never writes).
endpoint_hits: list[str] = []
if BACKEND_ROUTES_DIR.exists():
    for py in BACKEND_ROUTES_DIR.rglob('*.py'):
        if py.name == 'affinity_gift_spend.py':
            continue
        txt = py.read_text(encoding='utf-8', errors='ignore')
        for pat in ENDPOINT_PATTERNS:
            if re.search(pat, txt):
                endpoint_hits.append(f'{py}:{pat}')
record('no_gift_spend_endpoint', not endpoint_hits,
       f'unexpected endpoint refs: {endpoint_hits}')

# 8. No UI gift-spend button (grep frontend/app)
ui_hits: list[str] = []
if FRONTEND_APP_DIR.exists():
    for tsx in FRONTEND_APP_DIR.rglob('*.tsx'):
        txt = tsx.read_text(encoding='utf-8', errors='ignore')
        for pat in UI_BUTTON_PATTERNS:
            if re.search(pat, txt, re.IGNORECASE):
                ui_hits.append(f'{tsx}:{pat}')
record('no_gift_spend_ui_button', not ui_hits,
       f'unexpected UI button refs: {ui_hits}')

# 9. No adult/explicit tokens in policy or gift draft
raw_policy = POLICY_PATH.read_text(encoding='utf-8').lower() if POLICY_PATH.exists() else ''
gift_raw = GIFT_DRAFT_PATH.read_text(encoding='utf-8').lower() if GIFT_DRAFT_PATH.exists() else ''
for tok in ADULT_BLACKLIST:
    record(f'no_adult_token_policy:{tok}',
           tok not in raw_policy, f'policy contains token "{tok}"')
    record(f'no_adult_token_gift_draft:{tok}',
           tok not in gift_raw, f'gift draft contains token "{tok}"')

# 10. Source catalog exists
record('source_gift_draft_present', GIFT_DRAFT_PATH.exists(), str(GIFT_DRAFT_PATH))
record('source_gift_draft_referenced',
       policy.get('source_catalog') == 'affinity_gift_catalog_faction_element_draft_v1',
       f'got {policy.get("source_catalog")}')

# 11. Constraints assertions
ca = policy.get('constraints_assertions') or {}
for key, expected in [
    ('all_gift_value_tiers_borea_locked', True),
    ('all_affinity_tiers_borea_locked', True),
    ('all_tiers_stat_buff_live_false', True),
    ('no_endpoint_created_in_this_task', True),
    ('no_ui_button_created_in_this_task', True),
]:
    record(f'constraints_assertions_{key}', ca.get(key) == expected,
           f'expected {expected}, got {ca.get(key)!r}')


# Report
print('=' * 70)
print('AF2-B — Affinity Phase 2 Economy + Cap Policy Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
