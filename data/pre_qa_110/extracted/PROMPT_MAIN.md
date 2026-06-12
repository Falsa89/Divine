# PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_PACK

Execute after the pre-QA repo ZIP audit PASS 1.

## Context

The repo ZIP audit found real blockers before manual QA. The current state must be treated as:

PRE_QA_NOT_READY_FIX_PACK_REQUIRED

This pack is a blocker cleanup pack. It is not a feature expansion pack and it must not activate live rewards, gacha, IAP, payments, premium currency, PvP rewards, Guild rewards, Event rewards, Battlepass rewards, AFK rewards, or public launch readiness.

## Required Authorization

Exact string required:

AUTORIZZO_PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP

Authorized only:
- quarantine/hide unsafe legacy player-facing routes and UI;
- fix server scope bridge/alias bugs;
- fix auth/server-select token compatibility;
- prevent account-wide team formation writes from player-facing frontend;
- quarantine legacy achievement claim;
- quarantine or hide live gacha;
- player menu cleanup/hide false-ready/dev/QA/deferred surfaces;
- create validators/smoke/report;
- no broad production DB writes;
- no destructive migration.

Not authorized:
- gacha live;
- IAP/payment/store;
- premium/hard currency spend/grant;
- reward_live_general=true;
- account-wide roster/team/reward/economy mutations;
- guild/arena/event/pvp rewards live;
- battlepass/AFK rewards live;
- release/public launch claim;
- battle_engine rewrite;
- broad DB write;
- destructive migration.

## Blockers to Fix

### P0-A — Gacha live and visible

Findings:
- Backend exposes POST /api/gacha/pull and POST /api/gacha/pull10.
- These paths spend users.gems and insert into user_heroes without server_id.
- Frontend tab/menu Evoca calls /api/gacha/pull and /api/gacha/pull10.

Required outcome:
- In closed alpha pre-QA, gacha must not be live or player-facing.
- Quarantine backend gacha mutation endpoints by default.
- Hide/disable Evoca tab/menu/player-facing entry.
- If a preview/catalog remains, it must be explicitly read-only/preview/gated and must not spend gems or grant heroes.
- Return honest blocker code, e.g. GACHA_LIVE_DISABLED_PRE_QA or GACHA_SERVER_SCOPE_REQUIRED.
- No gems spend, no hero grant, no user_heroes account-wide mutation.

### P0-B — Team formation account-wide

Findings:
- Frontend player-facing Battle screen uses /api/team and /api/team/update-formation without server_id.
- Backend db.teams uses user_id + is_active only.
- Strict read endpoint exists but player-facing frontend does not use it.

Required outcome:
- Player-facing team formation must use server_id.
- Either wire frontend to strict server-scoped endpoints or disable legacy save/update and show honest blocker.
- Legacy account-wide team update must not be player-facing in closed alpha.
- No silent s1 fallback.
- Smoke must prove S1 team formation cannot leak to S2.

### P0-C — useServerScope mismatch

Findings:
- useServerScope exposes selected_server_id.
- Several Pack 98-108 components read serverId.
- This can make safe/gated components unreachable or not render.

Required outcome:
- Provide backward-compatible alias: serverId and selected_server_id must both resolve consistently.
- Prefer canonical selected_server_id, but support serverId alias.
- Update key components or hook safely.
- No silent default to s1.
- Null/no server must remain explicit NO_SERVER_SELECTED.

Components to check:
- DailyHomeRewardSection
- DailyLoginClaimButton
- DailyQuestClaimButton
- DailyTaskLoopOverview
- TowerStrictConsumer
- EconomyStrictConsumer
- ControlledRewardsConsumer
- PlayableLoopConsumer
- any frontend server-scoped consumer.

### P0/P1-D — Login/Auth token split

Findings:
- There are two AuthContext implementations:
  frontend/context/AuthContext.tsx
  frontend/src/auth/AuthContext.tsx
- Main login uses AsyncStorage token.
- Server screen uses SecureStore v96_auth_token for /api/psp/ensure and /api/psp/starter/claim.

Required outcome:
- Server select/PSP ensure must work after the main login path.
- Implement compatibility bridge/read both token locations or centralize token helper.
- Do not break existing auth.
- No security downgrade or plaintext debug secrets.
- Smoke/test script must prove login token path can reach PSP ensure/server selection helper.

### P0/P1-E — Player menu false-ready/dev/QA/deferred exposure

Findings:
Menu exposes too many unsafe/deferred/dev surfaces:
- Evoca/Gacha
- Arena PvP
- Battle Pass
- Shop/Item Shop/VIP
- legacy Guild
- GvG
- Raid
- Territory
- Piazza/DM
- Eventi
- Live/Guild QA
- Playability QA
- Battle Preview QA

Required outcome:
- Closed alpha player menu must not show false-ready systems.
- Hide or mark locked/deferred with honest state.
- Dev/QA screens must be hidden behind dev flag, not player-facing.
- Gacha/IAP/payment/VIP/Battlepass must not be live/player-facing.
- Preserve routes internally if needed; remove player-facing entry only.
- Frontend flags default OFF.
- No false-ready labels.

### P0-F — Legacy achievement claim bypass

Findings:
- POST /achievements/claim still exists.
- It uses legacy rewards gold/gems/stamina and mutates users.
- This bypasses Pack 106 controlled achievement claim.

Required outcome:
- Quarantine legacy achievement claim by default.
- Return ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED or ACHIEVEMENT_CONTROLLED_CLAIM_REQUIRED.
- No gold/gems/stamina user mutation.
- Controlled rewards Pack 106 achievement path remains preserved.

### P0/P1-G — Mutating legacy route allowlist

Findings:
- game_systems.py still registers many legacy mutating systems alongside strict routes.
- Potential mutating areas include economy/items/forge/raids/cosmetics/gvg/social/unique_items/level_sharing/achievements.

Required outcome:
- Create a closed-alpha mutating route allowlist/blocklist audit.
- Do not disable everything blindly if it breaks app startup.
- For player-facing unsafe mutation routes, add default fail-closed blockers.
- At minimum, validate no unsafe endpoints are reachable from visible player menu.
- Document remaining legacy routes as:
  allowed_safe
  internal_only
  dev_only
  legacy_quarantined
  deferred_blocker
  requires_future_pack

## Required Tracks

A Read official PASS1 audit report and current repo.
B Baseline 3-run suite and flakiness classification.
C Gacha backend quarantine + frontend Evoca hide/lock.
D Team formation server-scope fix or legacy blocker.
E useServerScope alias/consumer fix.
F Auth token compatibility bridge for Server Select/PSP ensure.
G Menu false-ready/dev/QA/deferred cleanup.
H Legacy achievements claim quarantine.
I Mutating route allowlist/blocklist validator.
J Runtime smoke E2E.
K Static anti-leak guard.
L Data invariants / forbidden mutation proof.
M Pack 91-109 + QA Kickoff preservation.
N Final 3-run master suite.
O Final report.

## Required Smoke E2E

Create:
backend/scripts/smoke_pre_qa_stabilization_110_alpha_blocker_cleanup.py

Smoke must prove:
1. gacha pull and pull10 blocked by default.
2. Evoca/gacha not visible in player closed-alpha menu or is locked/deferred honestly.
3. legacy achievements claim blocked and cannot grant gold/gems/stamina.
4. controlled rewards Pack 106 route still present/health OK.
5. team formation player path requires server_id or uses strict server-scoped path.
6. S1 team does not leak to S2.
7. useServerScope returns selected_server_id and serverId consistently.
8. no silent s1 fallback.
9. Server select/PSP ensure token helper can use main login token or compatible stored token.
10. dev/QA surfaces hidden unless dev flag explicitly ON.
11. reward_live_general=false.
12. release_readiness_claimed=false.
13. public_launch_ready=false.
14. production_release_ready=false.
15. users.gold/gems/experience unchanged.
16. no premium/hard/gems grants.
17. no IAP/gacha/payment activation.
18. Pack 91-109 preservation rollups still PASS or deviations documented.

## Forbidden Scope

NO gacha live
NO gems spend/grant
NO hero grant from gacha
NO IAP/payment/store activation
NO premium/hard currency grant
NO reward_live_general=true
NO account-wide team formation player-facing write
NO account-wide user_heroes mutation from gacha
NO legacy achievement reward mutation
NO users.gold/gems/experience mutation
NO guild/arena/pvp/event/battlepass/AFK reward live
NO public launch claim
NO production release claim
NO battle_engine formula rewrite
NO broad production DB writes
NO destructive migration
NO fake_PASS
NO validator weakening
NO false READY labels

## Expected Verdicts

If all blockers are fixed:
PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_READY_FOR_REAUDIT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If some require a second pass:
PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_PARTIAL_BLOCKERS_REMAIN_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If unsafe:
PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_NOT_READY_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

## Final Report

Create:
docs/divine/112_PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_FINAL_REPORT.md

Must include:
- verdict
- commit hash
- git diff --stat
- baseline/final suite
- gacha quarantine proof
- team formation server-scope proof
- useServerScope fix proof
- auth token compatibility proof
- menu cleanup proof
- achievements legacy quarantine proof
- mutating route allowlist/blocklist
- runtime smoke E2E
- static anti-leak guard
- data invariants
- explicit no users.gold/gems/experience mutation
- explicit no gacha/IAP/payment activation
- explicit no reward_live_general
- explicit Pack 91-109 + QA Kickoff preservation
- remaining blockers, if any
- next step: send updated repo ZIP for deep re-audit before manual QA.
