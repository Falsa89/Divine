# MEGA_RELEASE_ACCELERATION_107_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_SUPERPACK

Execute after Pack 106.

## Context
Pack 106 approved: controlled rewards ready/gated; S1/S2 isolation verified; users.gold/gems/experience unchanged; reward_live_general=false; release_readiness_claimed=false; baseline expected around 1695/36/0.

## Goal
Harden competitive/social/live-mode surfaces before closed alpha:
1. Audit and guard Arena/PvP server scope.
2. Audit and guard Guild server scope.
3. Audit and guard Event/live mode server scope.
4. Prevent cross-server ranking/guild/event leaks.
5. Keep competitive rewards deferred or ledger-gated OFF.
6. Add health/preflight endpoints and validators.
7. Add frontend guards/default OFF where needed.
8. Preserve Packs 91-106.
9. Keep reward_live_general=false and no release readiness claim.

## Required Authorization
Exact string required:
AUTORIZZO_V110_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_PACK_107

Authorized only: audits, guards, health/preflight routes for Arena/PvP/Guild/Event server-scope; server_id enforcement on safe read/preview endpoints; quarantine/blocker for unsafe legacy routes; ranking/guild/event reward locks; test writes on Pack 107 marked users only if needed for smoke; frontend gated guards/default OFF; smoke, validators, docs, final report.

Not authorized: PvP reward live; guild reward live; event reward live; battlepass reward live; AFK reward live; premium/hard grants; gems grants/spend; IAP/store/payment/gacha; broad production DB writes; destructive migration; legacy cleanup general; account-wide ranking/guild/event writes; release readiness claim.

If approval missing: MEGA_RELEASE_ACCELERATION_107_ARENA_GUILD_EVENTS_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Canonical Server-Scope Rules
All competitive/social/live mode state must be scoped by user_id + server_id + mode_scope.

Arena/PvP: MMR/rank/season/match history/opponent pool must be server-scoped. No S1 MMR/rank appears on S2. Rewards disabled/deferred or ledger-gated OFF.

Guild: membership/search/list/chat/events/war state must be server-scoped. No S1 guild membership appears on S2. Rewards disabled/deferred or ledger-gated OFF.

Events/live modes: progress/participation/ranking must be server-scoped. Live event rewards stay OFF/deferred unless existing controlled source and explicit scope. No global leaderboard leakage unless explicitly future-designed.

## Required Tracks
A Baseline 3-run suite and flakiness classification.
B Competitive/Social/Live Server-Scope SOT.
C Arena/PvP Legacy Path Audit.
D Arena/PvP Server-Scope Guards.
E Arena/PvP Reward Lock.
F Guild Legacy Path Audit.
G Guild Membership/Search/State Server-Scope Guards.
H Guild Reward Lock.
I Event/Live Mode Legacy Path Audit.
J Event/Live Mode Server-Scope Guards.
K Event/Live Reward Lock.
L Frontend Arena/Guild/Event Entry Guards.
M Cross-System Ranking/Leaderboard Anti-Leak Guard.
N Runtime Smoke E2E.
O Static Server-Scope Anti-Leak Guard.
P Data Invariants / Forbidden Mutation Proof.
Q Cleanup/Rollback.
R Live Readiness Update.
S MD5/Validator Rebase if needed, no weakening.
T Gate/Runtime Invariant Preservation.
U Final 3-run suite.
V Rollup Validator and Runner Integration.

## Required Blockers for Unsafe Legacy Routes
Use honest blockers: ARENA_SERVER_SCOPE_REQUIRED, ARENA_REWARD_LIVE_DISABLED, PVP_RANKING_SERVER_SCOPE_DEFERRED, GUILD_SERVER_SCOPE_REQUIRED, GUILD_REWARD_LIVE_DISABLED, EVENT_SERVER_SCOPE_REQUIRED, EVENT_REWARD_LIVE_DISABLED, LEADERBOARD_SERVER_SCOPE_REQUIRED. Do not silently fallback to s1. Do not claim filter_applied=true unless truly enforced.

## Runtime Smoke E2E Required Proof
Create backend/scripts/smoke_v110_pack_107_arena_pvp_guild_events_server_scope_e2e.py and prove: unmarked users refused; default guards OFF; S1/S2 PSP setup isolated; Arena status/ranking requires server_id or blocks; Arena S1 rank/MMR not on S2; Arena rewards blocked/deferred/OFF; Guild membership/search/list requires server_id or blocks; S1 guild membership not on S2; Guild rewards blocked/deferred/OFF; Event/live progress/ranking requires server_id or blocks; S1 event progress/rank not on S2; Event rewards blocked/deferred/OFF; leaderboard/static guards detect no unscoped active path; client cross-server access blocked; users.gold/gems/experience unchanged; no premium/hard/gems grant; no battlepass/event/AFK/PvP/guild rewards live unintentionally opened; Packs 91-106 preserved; cleanup verified.

## Forbidden Scope
NO Arena/PvP reward live; NO Guild reward live; NO Event reward live; NO Battlepass reward live; NO AFK reward live; NO reward_live_general=true; NO premium/hard currency grant; NO gems grant/spend; NO users.gold/gems/experience mutation; NO IAP/store/payment/gacha; NO account-wide ranking/guild/event writes; NO hardcoded server_id=s1; NO cross-server arena/guild/event leak; NO false filter_applied=true; NO broad production DB writes; NO destructive migration; NO legacy cleanup general execute; NO release readiness claim; NO fake_PASS; NO validator weakening; NO battle_engine formula rewrite; NO call to /api/battle/simulate from staging/live.

## Expected Verdicts
If guards/quarantines green: MEGA_RELEASE_ACCELERATION_107_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
If safe-read only and rewards deferred: MEGA_RELEASE_ACCELERATION_107_ARENA_GUILD_EVENTS_SERVER_SCOPE_READY_REWARDS_DEFERRED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
If unsafe cross-server leak remains: MEGA_RELEASE_ACCELERATION_107_ARENA_GUILD_EVENTS_CONDITIONAL_BLOCKERS_SERVER_SCOPE_OR_REWARD_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
Do not claim release readiness.

## Final Report
Create docs/divine/110_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_FINAL_REPORT.md and include: verdict; final commit hash; git diff --stat; baseline/final suite; flakiness classification; competitive/social/live SOT; Arena/PvP audit/status; Guild audit/status; Event/live audit/status; reward locks; frontend guards; leaderboard/ranking anti-leak proof; runtime smoke E2E; static anti-leak guard; data invariants; cleanup/rollback; live readiness update; MD5/validator rebase; gate preservation; explicit S1/S2 isolation for Arena/Guild/Event; explicit no users.gold/gems/experience mutation; explicit no premium/hard/gems grants; explicit no IAP/gacha/payment; explicit no Arena/Guild/Event/PvP reward live; explicit reward_live_general=false; explicit Pack 91-106 preservation; deferred blockers and next step.
