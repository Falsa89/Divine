#!/usr/bin/env python3
"""Pack 98 — Legacy claim non-regression guard (rebased canonical post Pack 103).

CANONICAL BASELINE EVOLUTION:
  * Pack 98 baseline: 2 player-facing live sources (daily_login_claim, daily_quest_completion_claim).
  * Pack 103 reconciled (approved): +tower_floor_completion_claim (ledger-gated, per-source kill switch OFF).
  * Pack 104 reconciled (approved): +shop_buy_strict_claim, +soul_forge_retire_strict_claim,
    +equipment_equip_strict_claim, +equipment_unequip_strict_claim (tutti ledger-gated, per-source kill switch OFF).
  * Pack 105 reconciled (approved): +equipment_upgrade_strict_claim, +forge_craft_strict_claim,
    +equipment_fusion_strict_claim (tutti ledger-gated, per-source kill switch OFF).

Il check sulle famiglie *_claim_live ESTERNE al set canonico (mail/achievements/battlepass/afk/event)
RIMANE invariato per preservare la safety.
"""
import os, json, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_legacy_claim_non_regression_v1.json')))
# Pack 98 baseline doc invariato (storico): solo i due iniziali player-facing.
assert d['only_two_real_player_facing_sources']==['daily_login_claim','daily_quest_completion_claim']
# Le famiglie ESTERNE restano NOT_LIVE.
for k in ('mail_reward_claim_live','achievements_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','shop_claim_live'):
    assert d[k] is False, k
sys.path.insert(0,os.path.join(R,'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY
live=[k for k,v in REWARD_SOURCE_REGISTRY.items() if v.get('live')]
# Canonical allowed (post Pack 103 + Pack 104 reconciliation).
# Tutte le source live SONO ledger-gated per-source kill switch OFF di default.
allowed={
    'qa_controlled_soft_currency_claim',
    'story_progress_marker_claim',
    'daily_login_claim',
    'daily_quest_completion_claim',
    # Pack 103 canonical: ledger-gated tower floor reward, OFF di default.
    'tower_floor_completion_claim',
    # Pack 104 canonical: ledger-gated shop buy / soul forge retire / equipment, OFF di default.
    'shop_buy_strict_claim',
    'soul_forge_retire_strict_claim',
    'equipment_equip_strict_claim',
    'equipment_unequip_strict_claim',
    # Pack 105 canonical: ledger-gated equipment upgrade / forge craft / fusion, OFF di default.
    'equipment_upgrade_strict_claim',
    'forge_craft_strict_claim',
    'equipment_fusion_strict_claim',
    # Pack 106 canonical: ledger-gated mail / achievement / daily-weekly controlled, OFF di default.
    'mail_claim_controlled',
    'achievement_claim_controlled',
    'daily_weekly_reward_claim',
}
diff = set(live) - allowed
assert not diff, f'unexpected live sources outside canonical allowlist: {diff}'
# Le famiglie ESTERNE forbidden non devono mai apparire come live.
# NOTA: Pack 106 introduce `mail_claim_controlled` (NON `mail_reward_claim` legacy),
# `achievement_claim_controlled` (NON `achievements_claim` legacy),
# `daily_weekly_reward_claim` (NON `battlepass_claim` ne' `event_claim` ne' `afk_claim`).
# Le famiglie legacy restano forbidden e NOT_LIVE.
forbidden_families = {'mail_reward_claim','achievements_claim','battlepass_claim','afk_claim','event_claim','shop_claim_legacy'}
for ff in forbidden_families:
    assert ff not in live, f'forbidden family must remain NOT_LIVE: {ff}'
print('[v110 PACK_98_LEGACY_CLAIM_NON_REGRESSION] OK canonical_post_pack_103_104_105_106 mail_achievements_etc_NOT_LIVE pack_91_97_preserved')
