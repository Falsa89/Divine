# MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SUPERPACK

Execute after Pack 104.

## Context

Pack 104 approved:
- Shop Buy Strict = READY_GATED.
- Soul Forge Retire Strict = READY_GATED.
- Equipment Equip/Unequip Strict = READY_GATED.
- Forge/Upgrade/Fusion = DEFERRED HONEST with blockers FORGE_UPGRADE_STRICT_DEFERRED and EQUIPMENT_FUSION_STRICT_DEFERRED.
- Economy strict writes are PSP/server-scoped and test-gated.
- users.gold/users.gems/users.experience unchanged.
- client price/reward payload ignored.
- reward_live_general=false.
- release_readiness_claimed=false.
- Baseline expected around 1662/36/0.
- Caveat: previous summary/report commit mismatch; Pack 105 final report must use one consistent final commit hash.

## Goal

SUPERPACK 105 closes the Pack 104 deferred blocker:
1. Define PSP material storage and strict material ledger rules.
2. Implement equipment upgrade strict if safe.
3. Implement forge strict if safe.
4. Implement equipment fusion strict if safe, or keep specific honest blocker if insufficient schema.
5. Ensure all spends are server-side priced, idempotent, PSP/server-scoped.
6. Use ledger/idempotency for mutating spend/write paths.
7. Preserve shop/soul/equipment strict from Pack 104.
8. No premium/hard currency grant.
9. No reward_live_general.
10. No release readiness claim.

## Approval

Required exact authorization string:
AUTORIZZO_V110_FORGE_UPGRADE_FUSION_PSP_MATERIAL_LEDGER_SPEND_PACK_105

Authorized only:
- PSP material storage design and strict loader.
- Equipment upgrade strict path.
- Forge strict path.
- Equipment fusion strict path only if schema is safely server-scoped.
- Ledger/idempotency for material/currency spend and result grants.
- Test writes on Pack 105 marked users only.
- Smoke, validators, docs, frontend guard.

Not authorized:
- reward live activation generale
- premium/hard currency grant
- gems grant/spend unless already explicitly account-global and NOT touched here
- IAP/store/payment/gacha
- mail/achievements/battlepass/events/AFK rewards live
- broad production DB writes
- destructive migration
- legacy cleanup general
- account-wide inventory/equipment/material writes
- release readiness claim

If approval missing:
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Required Canon

All material/equipment/forge/fusion state must be server-scoped:
- user_id + server_id + material_id
- user_id + server_id + equipment_instance_id
- user_id + server_id + hero_instance_id where relevant
- user_id + server_id + operation_id/idempotency_token

Preferred storage:
- player_server_profiles.soft_currencies
- player_server_profiles.materials or player_server_profiles.inventory.materials
- player_server_profiles.equipment_instances
- player_server_profiles.equipment_loadouts/equipped state

No strict path may mutate:
- users.gold
- users.gems
- users.experience
- account-wide inventory
- account-wide equipment
- account-wide materials

## Operation Rules

Equipment Upgrade Strict:
- endpoint example POST /api/economy/strict/equipment/upgrade?server_id=<sid>
- auth required
- server_id required
- PSP required
- equipment_instance_id required and must belong to user_id + server_id
- idempotency_token required
- server-side cost table only
- client cost/reward payload ignored
- consume PSP materials/soft currencies only
- increase equipment level/stat only in PSP/server-scoped equipment record
- replay same token returns idempotent result without double spend/upgrade
- max level cap enforced

Forge Strict:
- endpoint example POST /api/economy/strict/forge/craft?server_id=<sid>
- auth required
- recipe_id required
- recipe catalog server-side only
- idempotency_token required
- consume PSP materials/soft currencies only
- grant PSP server-scoped equipment/material only
- no premium/hard grants
- replay no duplicate grant/spend

Fusion Strict:
- endpoint example POST /api/economy/strict/equipment/fusion?server_id=<sid>
- only implement if equipment instances and consumed items are fully server-scoped
- require all consumed equipment belong to same user_id + server_id
- idempotency_token required
- no cross-server consume
- no account-wide consume
- if schema ambiguous, return honest blocker EQUIPMENT_FUSION_STRICT_DEFERRED_SCHEMA_AMBIGUOUS

## Required Tracks

A Baseline 3-run suite.
B PSP Material Storage SOT.
C Material/Equipment Schema Audit.
D Equipment Upgrade Strict Path.
E Forge Craft Strict Path.
F Equipment Fusion Strict Path or Honest Deferred Blocker.
G Ledger Spend/Idempotency Layer.
H Server-Side Cost/Recipe Catalog.
I Frontend Forge/Upgrade/Fusion Guard.
J Kill Switches and Flags.
K Runtime Smoke E2E.
L Static Material/Forge Anti-Leak Guard.
M Legacy Economy Non-Regression Audit.
N Data Invariants / Forbidden Mutation Proof.
O Cleanup/Rollback.
P Live Readiness Update.
Q MD5/Validator Rebase if needed, no weakening.
R Gate/Runtime Invariant Preservation.
S Final 3-run Suite.
T Rollup Validator and Runner Integration.

## Smoke E2E Required Proof

Create:
backend/scripts/smoke_v110_pack_105_forge_upgrade_fusion_strict_e2e.py

Prove:
1. unmarked users refused
2. all new kill switches OFF by default
3. S1/S2 PSP material/equipment isolation
4. seed Pack 105 test materials/equipment only on S1
5. equipment upgrade S1 consumes S1 materials/soft currency only
6. equipment upgrade replay same token no double spend/upgrade
7. equipment upgrade S2 cannot use S1 equipment/materials
8. forge craft S1 consumes server-side recipe cost only
9. forge craft replay no duplicate grant/spend
10. client price/reward payload ignored
11. premium/hard payload blocked/ignored
12. users.gold/gems/experience unchanged
13. fusion either works safely with no cross-server consume or returns honest blocker
14. Pack 104 shop/soul/equip still pass
15. Pack 91-104 preserved
16. cleanup verified

## Kill Switches Suggested

- ECONOMY_STRICT_WRITE_ENABLED=false existing/global
- EQUIPMENT_UPGRADE_STRICT_ENABLED=false
- FORGE_CRAFT_STRICT_ENABLED=false
- EQUIPMENT_FUSION_STRICT_ENABLED=false
- REWARD_CLAIM_LEDGER_LIVE_ENABLED=false if needed for ledgered operations

All smoke toggles must be restored OFF.

## Forbidden Scope

NO reward live activation generale
NO premium/hard currency grant
NO gems grant/spend in Pack 105
NO IAP/store/payment/gacha
NO users.gold/gems/experience mutation
NO account-wide inventory/equipment/material writes
NO hardcoded server_id=s1
NO cross-server consume/grant/equip/upgrade/fusion
NO client price/reward/cost trust
NO non-idempotent repeat mutation
NO broad production DB writes
NO destructive migration
NO legacy cleanup general execute
NO battlepass/event/mail/achievement/AFK reward live
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

## Expected Verdicts

If upgrade + forge safe and fusion safe/deferred:
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If only preflight/audit is safe:
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_READY_NOT_APPLIED_PENDING_SCHEMA_APPROVAL_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If unsafe leak remains:
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_CONDITIONAL_BLOCKERS_MATERIAL_OR_SERVER_SCOPE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Do not claim release readiness.

## Final Report

Create:
docs/divine/110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_FINAL_REPORT.md

Must include:
- verdict
- final commit hash, consistent across summary and report
- git diff --stat
- baseline/final suite
- PSP material storage SOT
- material/equipment schema audit
- equipment upgrade strict status
- forge craft strict status
- equipment fusion strict/deferred status
- ledger spend/idempotency proof
- server-side cost/recipe catalog
- frontend guard
- kill switches
- smoke E2E
- static anti-leak guard
- data invariants
- cleanup/rollback
- live readiness update
- MD5/validator rebase
- gate preservation
- explicit S1/S2 isolation
- explicit no users.gold/gems/experience mutation
- explicit no premium/hard grants
- explicit no IAP/gacha/payment
- explicit reward_live_general=false
- explicit Pack 91-104 preservation
- deferred blockers and next step
