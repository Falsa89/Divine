# MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_SUPERPACK

Execute after Pack 103 reconciliation approval.

## Context

Pack 103 + reconciliation approved:
- Tower execute controlled READY.
- `tower_floor_completion_claim` ledger/idempotency path validated.
- `tower_floor_clear_success -> daily_quest_2` server-side hook validated.
- S1/S2 isolation verified.
- `users.gold/users.gems/users.experience` not mutated by Tower path.
- `reward_live_general=false`.
- `release_readiness_claimed=false`.
- Caveat: Pack 103 introduced +5 legacy/by-design validator FAILs because old “absence guards” still expect no tower reward source/daily quest 2 hook. Pack 104 must reconcile/rebase these canonical validator expectations without weakening safety.

Baseline expected after reconciliation:
- approximately `1657/41/0`, unless Pack 104 first normalizes canonical Pack 103 validator baseline.

## Goal

SUPERPACK 104 closes the main economy/progression write paths that remain unsafe or deferred:
1. Shop buy strict server-scoped write path.
2. Soul Forge retire strict server-scoped write path.
3. Equipment equip/unequip/upgrade strict write paths.
4. Forge/fusion strict write preflight or controlled runtime if safe.
5. Inventory/currency PSP/server-scope enforcement.
6. Ledger/idempotency for mutating economy writes.
7. Frontend guarded consumers for shop/soul/equipment/forge.
8. Reconcile canonical validator baseline after Pack 103 so by-design FAILs do not accumulate.
9. No IAP, no gacha, no premium/hard currency grants, no release readiness.

## Approval

Required exact authorization string:
AUTORIZZO_V110_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_PACK_104

Authorized only:
- server-scoped shop buy for non-premium items/currencies already approved as soft/server-bound;
- soul forge retire server-scoped controlled path;
- equipment equip/unequip/upgrade strict PSP/inventory path;
- forge/fusion strict preflight and controlled runtime only if fully server-scoped/idempotent;
- idempotency ledger or per-action ledger for mutating economy writes;
- frontend guard/preview for shop/soul/equipment/forge;
- validator reconciliation of Pack 103 canonical by-design changes;
- test writes on Pack 104 marked users only;
- smoke, validators, docs, final report.

Not authorized:
- IAP/store/payment integration;
- gacha changes;
- premium/hard currency grants;
- real-money purchases;
- broad production DB writes;
- destructive migration;
- legacy cleanup general;
- account-wide inventory/currency/equipment writes;
- battlepass/event/mail/achievement/AFK reward live;
- release readiness claim.

If approval missing:
MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Canonical Scope Rules

All gameplay economy state is server-scoped unless explicitly account-global by design.

Strict keys:
- currency/inventory: `user_id + server_id + item_id/currency_id`
- equipment ownership: `user_id + server_id + equipment_instance_id`
- equipped state: `user_id + server_id + hero_instance_id + slot`
- soul forge retire: `user_id + server_id + hero_instance_id + idempotency_token`
- shop buy: `user_id + server_id + shop_id + item_id + purchase_key/idempotency_token`

Forbidden in strict write paths:
- silent `server_id="s1"`;
- account-wide fallback;
- `users.gold/users.gems/users.experience` mutation;
- hard/premium currency grant;
- client-supplied reward payload;
- non-idempotent repeat purchases/retire/upgrade.

## Required Tracks

A — Baseline and Pack 103 Canonical Fail Reconciliation
- Run baseline suite 3x.
- Identify the +5 legacy/by-design FAILs from Pack 103.
- Rebase them only if they contradict the now-approved canonical state: tower_floor_completion_claim exists, daily_quest_2 hook exists, Tower ledger-gated source is allowed.
- Do NOT weaken safety guards: they must still forbid reward_live_general, premium, users.* mutation, non-ledger tower reward, client spoofing.
- Output canonical baseline reconciliation doc.

B — Economy Strict Write SOT
- Create/update SOT for shop/soul/equipment/forge strict writes.
- Define server-scoped keys, ledgers, idempotency, forbidden account-wide writes.

C — Shop Buy Strict Path
- Audit existing shop/item-shop routes.
- Implement or correct strict buy endpoint only for safe non-premium server-bound items.
- Required: auth, server_id, PSP, idempotency_token/purchase_key, server-side price, server-side catalog, cap checks, ledger.
- No client price/payload trust.
- No hard/premium currency grant.
- If unsafe, return blocker `SHOP_BUY_STRICT_LEDGER_REQUIRED`.

D — Soul Forge Retire Strict Path
- Audit existing soul forge retire.
- Ensure hero ownership is server-scoped.
- Retire writes only PSP/server-bound soul essence or approved soft materials.
- Requires idempotency token.
- No cross-server hero retire.
- No premium grants.
- No duplicate retire reward.

E — Equipment Equip/Unequip Strict Path
- Ensure equipment ownership and hero ownership both match same user+server.
- equip/unequip writes server-scoped state only.
- No account-wide equipment fallback.
- No cross-server equip.
- Idempotent repeated equip/unequip.

F — Equipment Upgrade / Forge / Fusion Strict Path
- Audit upgrade/forge/fusion write routes.
- Implement controlled strict path only if all material/currency/equipment inputs are server-scoped and idempotent.
- If not safe, produce honest blockers:
  `FORGE_UPGRADE_STRICT_DEFERRED`
  `EQUIPMENT_FUSION_STRICT_DEFERRED`
- No premium/hard grant.

G — Inventory/Currency Server-Scope Cross Guard
- Verify all touched economy writes use PSP/server-scoped inventory/currencies.
- No `users.gold/users.gems/users.experience` mutation from Pack 104 routes.
- No account-wide inventory writes.

H — Frontend Consumer Guards
- Shop, Soul Forge, Equipment, Forge screens must pass selected server_id.
- No silent s1.
- Show locked/deferred for routes not yet safe.
- No false success UI.
- Refetch inventory/currency/equipment after successful writes.
- UI default flags can remain OFF if needed.

I — Kill Switches / Flags
Suggested defaults OFF:
- `SHOP_BUY_STRICT_ENABLED=false`
- `SOUL_FORGE_RETIRE_STRICT_ENABLED=false`
- `EQUIPMENT_STRICT_WRITES_ENABLED=false`
- `FORGE_STRICT_WRITES_ENABLED=false`
- Any test-only flag must reset OFF after smoke.

J — Runtime Smoke E2E
Create:
`backend/scripts/smoke_v110_pack_104_shop_soul_equipment_forge_strict_writes_e2e.py`

Smoke must prove at minimum:
1. unmarked users refused;
2. kill switches OFF by default;
3. S1/S2 PSP/inventory/currency/equipment isolation;
4. shop buy S1 consumes server-side price and grants only server-bound item/currency;
5. shop buy replay same token no duplicate;
6. shop buy S2 unaffected;
7. soul forge retire S1 consumes only S1 hero and grants S1 soul essence/material;
8. soul forge replay no duplicate;
9. soul forge cannot retire S2 hero from S1;
10. equipment equip/unequip S1 does not affect S2;
11. equipment upgrade/forge either safe and idempotent or honestly deferred;
12. client payload price/reward ignored;
13. premium/hard payload blocked/ignored;
14. `users.gold/gems/experience` unchanged;
15. Packs 91-103 preserved;
16. cleanup verified.

K — Static Economy Anti-Leak Guard
Fail if:
- route writes `users.gold/users.gems/users.experience`;
- active strict economy path lacks server_id;
- hardcoded `server_id="s1"`;
- client price/reward trusted;
- premium/hard grant possible;
- non-idempotent repeat purchase/retire/upgrade;
- account-wide inventory/equipment writes;
- fake_PASS or validator weakening.

L — Legacy Economy Non-Regression Audit
Audit and classify:
- shop buy/item shop;
- soul forge;
- equipment;
- forge/fusion;
- inventory;
- currencies;
- tower rewards;
- daily rewards;
- mail/achievements/battlepass/events/AFK.

M — Data Invariants / Forbidden Mutation Proof
Confirm:
- no broad production grants;
- no unmarked test writes;
- no premium/hard grants;
- no reward_live_general;
- no gacha/IAP/payment;
- no destructive migration;
- no legacy cleanup general;
- Pack 91-103 preserved.

N — Cleanup / Rollback
Create cleanup for Pack 104 marked artifacts; dry-run default, `--apply` required.

O — Live Readiness Update
Allowed only:
- `shop_buy_strict_ready=true` if smoke green;
- `soul_forge_retire_strict_ready=true` if smoke green;
- `equipment_strict_writes_ready=true` if smoke green;
- `forge_strict_ready` only if fully safe; otherwise deferred;
- `reward_live_general=false`;
- `premium_grants=false`;
- `release_readiness_claimed=false`.

P — MD5 / Validator Rebase
Rebase canonical Pack 103/104 changes only with historical references preserved.
No validator weakening.

Q — Gate/Runtime Invariant Preservation
Preserve Packs 84-103.
No battle_engine rewrite.
No /api/battle/simulate regression.
No fake_PASS.

R — Final 3-run Suite
Required=0, Miss=0, deterministic. Optional/legacy fails must be reconciled or honestly explained.

S — Rollup Validator and Runner Integration
Create rollup:
`validate_mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup.py`
Register sentinel:
`PUBLIC_SYNC_TAG_v110_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_SUPERPACK`

## Forbidden Scope

NO IAP/store/payment integration
NO gacha changes
NO premium/hard currency grant
NO real-money purchase path
NO users.gold/gems/experience mutation from Pack 104 routes
NO account-wide inventory/currency/equipment writes
NO hardcoded server_id=s1
NO cross-server equip/retire/buy/upgrade
NO client price/reward trust
NO non-idempotent repeat mutation
NO broad production DB writes
NO destructive migration
NO legacy cleanup general execute
NO battlepass/event/mail/achievement/AFK reward live
NO reward_live_general=true
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

## Expected Verdicts

If shop/soul/equipment strict writes are green and forge safely deferred or green:
MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If only audit/preflight is safe:
MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_READY_NOT_APPLIED_PENDING_RUNTIME_APPROVAL_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If economy leak remains:
MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_CONDITIONAL_BLOCKERS_ECONOMY_OR_SERVER_SCOPE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Do not claim release readiness.

## Final Report

Create:
`docs/divine/110_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_FINAL_REPORT.md`

Must include:
- verdict;
- final commit hash;
- git diff --stat;
- baseline/final suite;
- Pack 103 canonical fail reconciliation;
- shop buy strict path;
- soul forge retire strict path;
- equipment equip/unequip strict path;
- equipment upgrade/forge/fusion status;
- inventory/currency server-scope proof;
- frontend guards;
- kill switches;
- smoke E2E;
- static anti-leak guard;
- data invariants;
- cleanup/rollback;
- live readiness update;
- MD5/validator rebase;
- gate preservation;
- explicit S1/S2 isolation;
- explicit no users.gold/gems/experience mutation;
- explicit no premium/hard grants;
- explicit no IAP/gacha/payment;
- explicit reward_live_general=false;
- explicit Pack 91-103 preservation;
- deferred blockers and next step.
