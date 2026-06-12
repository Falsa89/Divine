# MEGA_RELEASE_ACCELERATION_108_GUILD_SERVER_SCOPE_RETROFIT_AND_FRONTEND_PLAYABLE_LOOP_POLISH_SUPERPACK

Execute after Pack 107.

## Context

Pack 107 approved:
- Arena/PvP/Event safe by absence / rewards deferred.
- Guild legacy exists but is NOT server-scoped.
- Pack 107 was audit/guard-only and did not retrofit Guild.
- Competitive/social/event rewards remain OFF.
- S1/S2 isolation verified for guard/preflight surfaces.
- reward_live_general=false.
- release_readiness_claimed=false.
- users.gold/gems/experience unchanged.
- Pack 91-106 preserved.
- Baseline expected around 1706/36/0.

Pack 108 is the last functional hardening/polish pack before Closed Alpha RC Sweep.

## Goal

SUPERPACK 108 performs Guild server-scope retrofit and frontend playable loop polish:
1. Retrofit or quarantine Guild legacy routes so no player-facing guild path is account-wide.
2. Implement server-scoped Guild membership/search/status preview safely where feasible.
3. Keep Guild rewards OFF/deferred.
4. Ensure Arena/PvP/Event remain locked/deferred and do not regress.
5. Polish frontend playable loop entrypoints for Home/Lobby/Daily/Tower/Shop/Forge/Rewards/Guild with guarded/default-OFF flags.
6. Ensure server switching refreshes visible state and never silently uses s1.
7. Produce an alpha navigation/readiness map without claiming release readiness.
8. Preserve Packs 91-107.
9. Keep reward_live_general=false.
10. Do not claim release readiness.

## Required Authorization

Exact string required:
AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_PACK_108

Authorized only:
- Guild server-scope retrofit/preflight/quarantine;
- server_id enforcement on safe Guild read/preview endpoints;
- server-scoped guild membership/search/status if safe;
- blocking/quarantine of unsafe guild legacy routes;
- frontend guarded playable loop polish;
- frontend state labels for locked/deferred/ready_gated modes;
- no reward live;
- test writes on Pack 108 marked users only if required for guild smoke;
- smoke, validators, docs, final report.

Not authorized:
- guild reward live;
- Arena/PvP/Event reward live;
- battlepass reward live;
- AFK reward live;
- premium/hard currency grant;
- gems grants/spend;
- IAP/store/payment/gacha;
- broad production DB writes;
- destructive migration;
- legacy cleanup general;
- account-wide guild writes;
- release readiness claim.

If approval missing:
MEGA_RELEASE_ACCELERATION_108_GUILD_FRONTEND_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Canonical Rules

Guild:
- Guild membership must be scoped by user_id + server_id + guild_id.
- Guild identity/list/search must include server_id unless explicitly global directory is introduced in a future pack.
- No S1 guild membership appears on S2.
- Guild chat/war/events/rewards must remain deferred or blocked if not server-scoped.
- Legacy account-wide guild paths must be quarantined/blockered, not silently used.
- Guild reward live remains false.

Frontend Playable Loop:
- Home/Lobby must not show false-ready systems.
- All playable/gated modules must use selected server_id.
- No silent default server_id='s1'.
- Server switch must refetch/refresh state.
- Locked/deferred/preview/ready_gated states must be clear.
- UI flags default OFF for sensitive surfaces.
- No false reward success.

## Required Tracks

A Baseline 3-run suite and flakiness classification.
B Guild Server-Scope Retrofit SOT.
C Guild Legacy Route Audit.
D Guild Membership Schema/Storage Server-Scope.
E Guild Search/List/Status Strict Endpoints.
F Guild Legacy Quarantine / Blocker Routes.
G Guild Reward Lock.
H Arena/PvP/Event Guard Preservation.
I Frontend Playable Loop Map.
J Frontend Home/Lobby/Daily/Tower/Shop/Forge/Rewards/Guild Guards.
K Server Switch / Selected Server Refresh Guard.
L Locked/Deferred/Ready-Gated UI Copy Audit.
M Runtime Smoke E2E.
N Static Guild/Frontend Anti-Leak Guard.
O Data Invariants / Forbidden Mutation Proof.
P Cleanup/Rollback.
Q Live Readiness Update.
R MD5/Validator Rebase if needed, no weakening.
S Gate/Runtime Invariant Preservation.
T Final 3-run suite.
U Rollup Validator and Runner Integration.

## Required Guild Blockers

For unsafe legacy paths, return/document:
- GUILD_SERVER_SCOPE_REQUIRED
- GUILD_LEGACY_QUARANTINED
- GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED
- GUILD_CHAT_SERVER_SCOPE_DEFERRED
- GUILD_WAR_SERVER_SCOPE_DEFERRED
- GUILD_REWARD_LIVE_DISABLED

Do not use false filter_applied=true.
Do not fallback to s1.

## Frontend Surfaces To Guard/Polish

At minimum audit/guard:
- Home daily rewards / daily task loop;
- Tower strict catalog/execute/reward flow;
- Economy strict shop/soul/equipment/forge;
- Controlled rewards mail/achievements/daily-weekly;
- Guild entry/status if added;
- Arena/PvP/Event entries as locked/deferred if not ready;
- Server selector and server switch behavior;
- Lobby/pre-battle entrypoints.

Default flags should remain OFF unless already explicitly intended:
- EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=false
- EXPO_PUBLIC_DAILY_HOME_UNLOCK=false
- EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED=false
- EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED=false
- EXPO_PUBLIC_GUILD_UI_ENABLED=false or equivalent
- EXPO_PUBLIC_ARENA_UI_ENABLED=false unless safe preview only
- EXPO_PUBLIC_EVENT_UI_ENABLED=false unless safe preview only

## Runtime Smoke E2E Required Proof

Create:
backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py

Prove at minimum:
1. unmarked users refused for mutating/test-only paths.
2. new guild/frontend flags OFF by default.
3. S1/S2 PSP/profile setup isolated.
4. Guild legacy unsafe route blocked/quarantined or no longer player-facing.
5. Guild membership/search/status strict path requires server_id.
6. Guild membership created/read on S1 does not appear on S2 if runtime membership implemented.
7. Guild rewards remain OFF/deferred.
8. Arena/PvP/Event reward locks from Pack 107 remain.
9. Home/Lobby guarded map returns no false-ready systems.
10. Daily/Tower/Economy/Rewards entrypoints still use selected server_id.
11. Server switch S1->S2 refresh proof or static guard proof.
12. users.gold/gems/experience unchanged.
13. no premium/hard/gems grants.
14. no IAP/gacha/payment.
15. reward_live_general=false.
16. release_readiness_claimed=false.
17. Packs 91-107 preserved.
18. cleanup verified.

## Forbidden Scope

NO guild reward live
NO Arena/PvP/Event reward live
NO battlepass reward live
NO AFK reward live
NO reward_live_general=true
NO premium/hard currency grant
NO gems grant/spend
NO users.gold/gems/experience mutation
NO IAP/store/payment/gacha
NO account-wide guild writes
NO hardcoded server_id=s1
NO cross-server guild leak
NO false filter_applied=true
NO false frontend ready labels
NO broad production DB writes
NO destructive migration
NO legacy cleanup general execute
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

## Expected Verdicts

If Guild retrofit/quarantine + frontend loop guards are green:
MEGA_RELEASE_ACCELERATION_108_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If Guild runtime remains deferred but safely quarantined and frontend polish green:
MEGA_RELEASE_ACCELERATION_108_FRONTEND_PLAYABLE_LOOP_READY_GUILD_SERVER_SCOPE_READY_GATED_DEFERRED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If Guild cross-server or frontend false-ready leak remains:
MEGA_RELEASE_ACCELERATION_108_GUILD_FRONTEND_CONDITIONAL_BLOCKERS_SERVER_SCOPE_OR_FALSE_READY_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Do not claim release readiness.

## Final Report

Create:
docs/divine/110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_FINAL_REPORT.md

Must include:
- verdict
- final commit hash coherent between summary and report
- git diff --stat
- baseline/final suite
- flakiness classification if any
- Guild SOT
- Guild legacy audit/status
- Guild strict endpoints/quarantine status
- Guild reward lock
- Arena/PvP/Event preservation
- Frontend playable loop map
- Home/Lobby/Daily/Tower/Shop/Forge/Rewards/Guild guard status
- server switch refresh proof
- UI copy audit for locked/deferred/ready_gated states
- runtime smoke E2E
- static anti-leak guard
- data invariants
- cleanup/rollback
- live readiness update
- MD5/validator rebase
- gate preservation
- explicit S1/S2 isolation for Guild
- explicit no users.gold/gems/experience mutation
- explicit no premium/hard/gems grants
- explicit no IAP/gacha/payment
- explicit no Guild/Arena/PvP/Event rewards live
- explicit reward_live_general=false
- explicit release_readiness_claimed=false
- explicit Pack 91-107 preservation
- deferred blockers and next step
