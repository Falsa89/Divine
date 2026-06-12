# MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_AND_RELEASE_GATE_SUPERPACK

Execute after Pack 108.

## Context

Pack 108 approved:
- Guild strict read/preview is READY_GATED_DEFERRED.
- Guild legacy mutating routes are quarantined 423.
- Guild rewards remain OFF / GUILD_REWARD_LIVE_DISABLED.
- Frontend playable loop map is polished with no false-ready labels.
- Server switch refresh guard prevents silent s1 fallback.
- S1/S2 guild isolation verified.
- Arena/PvP/Event rewards OFF.
- reward_live_general=false.
- release_readiness_claimed=false.
- Suite baseline expected around 1722/36/0.

Packs 91-108 created the safe/gated foundation for:
- PSP/server profiles and server-scoped gameplay state.
- Tower strict catalog/execute/claim.
- Daily login / daily quest loop.
- Economy strict shop/soul/equip/upgrade/forge/fusion.
- Controlled mail/achievement/daily-weekly rewards.
- Competitive/social/event guards.
- Guild strict read/preview + frontend playable loop.

## Goal

SUPERPACK 109 is the Closed Alpha Release Candidate Sweep.

This pack does NOT force release readiness.
It must produce an honest release gate report:
- READY
- CONDITIONAL_READY
- NOT_READY

The target is a closed/internal alpha candidate, not public launch.

## Required Authorization

Exact string required:
AUTORIZZO_V110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_PACK_109

Authorized only:
- repo-wide release gate audit;
- global smoke aggregation;
- validator suite cleanup;
- optional-fail classification;
- mobile QA checklist;
- closed alpha readiness report;
- frontend navigation/readiness map verification;
- explicit blocker matrix;
- docs/validators/report only, unless a tiny non-risky copy/label fix is needed;
- no runtime reward/economy/IAP/gacha activation.

Not authorized:
- release readiness claim unless evidence supports at least CONDITIONAL_READY and report says exactly why;
- public launch claim;
- premium/hard currency grant;
- gems grants/spend;
- IAP/payment/store/gacha activation;
- PvP/Guild/Event/Battlepass/AFK reward live;
- broad production DB writes;
- destructive migrations;
- legacy cleanup general;
- battle_engine formula rewrite;
- changing deferred systems into live systems;
- fake_PASS or validator weakening.

If approval missing:
MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## RC Scope

Audit and report readiness for these areas:
1. Server/profile isolation.
2. Auth/logout/server selection.
3. Home/Lobby/playable loop map.
4. Story path and battle preview/staging path.
5. Tower strict loop.
6. Daily login + daily quest loop.
7. Controlled reward center.
8. Economy strict shop/soul/equipment/forge/fusion.
9. Inventory/equipment/material PSP scope.
10. Guild strict read/preview and guild legacy quarantine.
11. Arena/PvP/Event guards.
12. Frontend mobile QA routes and flags.
13. Reward ledger/idempotency.
14. Forbidden users.gold/gems/experience mutation guard.
15. No premium/IAP/gacha/payment live.
16. Remaining deferred blockers.

## Required Tracks

A Baseline 3-run suite and flakiness classification.
B Repo-wide Release Gate SOT.
C Pack 91-108 Preservation Rollup.
D Server/Profile Isolation Audit.
E Auth/Logout/Server Selection Audit.
F Frontend Navigation / Playable Loop RC Audit.
G Story/Battle Preview/Staging RC Audit.
H Tower RC Audit.
I Daily/Daily Quest/Controlled Rewards RC Audit.
J Economy Strict RC Audit.
K Inventory/Equipment/Material PSP RC Audit.
L Guild RC Audit.
M Arena/PvP/Event RC Audit.
N Reward Ledger/Idempotency RC Audit.
O Forbidden Mutation / Premium / Gacha / IAP Static Guard.
P Mobile QA Checklist and Manual Test Script.
Q Known Deferred Blocker Matrix.
R Closed Alpha Gate Verdict.
S Cleanup/Rollback/Artifacts Index.
T Final 3-run Master Suite.
U Rollup Validator and Runner Integration.
V Final Report + Next Plan.

## Important Rules

- Do not change reward live flags.
- Do not enable IAP/gacha/payment.
- Do not enable Guild live rewards.
- Do not enable Arena/PvP/Event rewards.
- Do not remove blockers just to pass.
- Do not mark NOT_READY blockers as READY.
- Optional fails may remain only if honestly classified as by-design/deferred/legacy and not blocking closed alpha.
- If any core invariant fails, verdict must be NOT_READY or CONDITIONAL_BLOCKERS.
- A closed alpha can be CONDITIONAL_READY with deferred Guild live, PvP rewards, Event rewards, IAP, Battlepass, AFK rewards, and public launch systems, as long as playable safe loop is coherent and documented.

## Required Global Smoke

Create:
backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py

Smoke must prove at least:
1. selected server required / no silent s1 fallback.
2. S1/S2 isolation on PSP profile.
3. Tower strict health/status/preview path green.
4. Daily login + daily quest loop green or correctly gated.
5. Controlled rewards health green and reward live general OFF.
6. Economy strict health/catalog green and mutating flags default OFF or test-only.
7. Guild strict health/preflight green and legacy mutating routes quarantined.
8. Arena/PvP/Event guards green/deferred.
9. Frontend playable loop map has no false-ready labels.
10. reward_live_general=false.
11. release_readiness_claimed=false unless final report explicitly sets RC gate state only.
12. users.gold/gems/experience unchanged after smoke.
13. premium/hard/gems grants not possible in controlled sources.
14. IAP/store/payment/gacha not activated.
15. Pack 91-108 rollups preserved.

## Release Gate Verdict Logic

Allowed final gate values:
- CLOSED_ALPHA_READY
- CLOSED_ALPHA_CONDITIONAL_READY
- CLOSED_ALPHA_NOT_READY

Use CLOSED_ALPHA_READY only if:
- required smoke green;
- no core runtime blocker;
- no server-scope leak;
- no reward/economy unsafe path;
- no false-ready UI;
- no critical mobile QA blocker.

Use CLOSED_ALPHA_CONDITIONAL_READY if:
- safe playable loop works;
- deferred systems are documented and gated;
- optional/by-design failures remain but do not block internal alpha;
- no core safety invariant fails.

Use CLOSED_ALPHA_NOT_READY if:
- server-scope leak remains;
- reward/economy leak remains;
- users.gold/gems/experience mutation risk remains;
- selected server fallback persists;
- frontend false-ready persists;
- auth/server selection is broken;
- suite has REQUIRED fail or MISS;
- smoke global fails.

## Forbidden Scope

NO public launch claim
NO production release claim
NO reward_live_general=true
NO premium/hard currency grant
NO gems grant/spend
NO users.gold/gems/experience mutation
NO IAP/store/payment/gacha activation
NO Guild reward live
NO Arena/PvP/Event reward live
NO Battlepass reward live
NO AFK reward live
NO broad production DB writes
NO destructive migration
NO legacy cleanup general execute
NO false READY state
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

## Expected Verdicts

If internal alpha safe but deferred systems remain:
MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_CONDITIONAL_READY_WITH_DEFERRED_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If fully ready for internal closed alpha:
MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If blocked:
MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_NOT_READY_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Final Report

Create:
docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md

Must include:
- verdict
- final commit hash coherent between summary and report
- git diff --stat
- baseline/final suite
- flakiness classification
- Pack 91-108 preservation matrix
- server/profile isolation audit
- auth/logout/server selection audit
- frontend playable loop audit
- story/battle preview/staging audit
- tower audit
- daily/daily quest/controlled rewards audit
- economy strict audit
- inventory/equipment/material audit
- guild audit
- arena/pvp/event audit
- reward ledger/idempotency audit
- forbidden mutation/premium/IAP/gacha guard
- mobile QA checklist
- known deferred blocker matrix
- closed alpha gate verdict: READY / CONDITIONAL_READY / NOT_READY
- explicit no users.gold/gems/experience mutation
- explicit no premium/hard/gems grants
- explicit no IAP/gacha/payment
- explicit no Guild/Arena/PvP/Event/Battlepass/AFK reward live
- explicit reward_live_general=false
- explicit public_launch_ready=false
- explicit production_release_ready=false
- recommended next step
