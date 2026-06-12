# CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_INTAKE_RUNBOOK

Execute after Pack 109 approval.

## Context

Pack 109 verdict:
MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_CONDITIONAL_READY_WITH_DEFERRED_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Canonical gate:
CLOSED_ALPHA_CONDITIONAL_READY

This is NOT public launch.
This is NOT production release.
This is an internal/manual closed alpha kickoff using the Pack 109 mobile QA checklist.

## Objective

Prepare and run the internal closed alpha manual QA process for at least 5 testers across iOS/Android, without enabling new live systems.

Goals:
1. Verify build/install/startup on real devices.
2. Verify auth/server selection/logout.
3. Verify no silent s1 fallback.
4. Verify Home/Lobby/playable loop navigation.
5. Verify Tower/Story/Daily/Rewards/Economy/Guild strict/gated flows.
6. Verify locked/deferred surfaces show honest states.
7. Collect tester feedback.
8. Classify bugs P0/P1/P2/P3.
9. Produce a closed alpha QA result report.
10. Recommend the next Pack 110 based on evidence.

## Required Authorization

Exact string:
AUTORIZZO_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_NO_RUNTIME_ACTIVATION

Authorized only:
- QA runbook/checklist execution;
- tester instructions;
- feedback templates;
- issue triage matrix;
- manual QA report;
- optional docs-only/read-only helpers;
- no runtime feature activation.

Not authorized:
- reward live activation;
- premium/hard currency grant;
- IAP/payment/store/gacha activation;
- Guild/Arena/PvP/Event/Battlepass/AFK reward live;
- broad DB writes;
- destructive migrations;
- release/public launch claim;
- changing deferred systems into live systems.

## Tester Target

Minimum:
- 5 internal testers total.
- At least 2 Android devices.
- At least 2 iOS devices if available, otherwise document iOS unavailable.
- At least one lower-end device if available.
- At least one fresh account.
- At least one returning account.
- At least one server switch test S1 -> S2 -> S1.

## Required QA Sections

A Install / startup
B Auth / logout
C Server selection / server switch
D Home / Lobby / navigation
E Story / battle preview/staging
F Tower strict loop
G Daily login / daily quest
H Controlled rewards
I Economy strict shop/soul/equipment/forge/fusion
J Inventory/equipment/material scope
K Guild strict / legacy quarantine
L Arena/PvP/Event locked/deferred state
M Performance / loading / crash / memory
N UI/UX mobile readability
O Safety invariants

## P0/P1/P2/P3 Bug Severity

P0:
- app cannot launch for most testers;
- login/server selection unusable;
- server-scope leak or silent s1 fallback;
- reward/economy mutation unsafe;
- users.gold/gems/experience unexpected mutation;
- premium/IAP/gacha/payment accidentally live;
- crash blocks core loop.

P1:
- core closed alpha flow blocked for many testers;
- Tower/Daily/Economy/Guild strict health unusable;
- major mobile layout break;
- data refresh inconsistent across server switch;
- repeated crash in a main flow.

P2:
- non-critical feature broken but workaround exists;
- confusing gated/deferred label;
- minor reward preview inconsistency with no mutation;
- intermittent UI/loading issue.

P3:
- text/copy issue;
- spacing/visual polish;
- minor non-blocking UX improvement.

## Required Report

Create:
docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md

Include:
- tester/device matrix;
- test window;
- build/source commit;
- Pack 109 gate reference;
- sections A-O results;
- P0/P1/P2/P3 issue table;
- screenshots/videos requested list;
- safety invariant confirmation;
- recommended Pack 110;
- decision: continue alpha / fix P0 first / fix P1 first / expand testers.

## Next Pack Decision Logic

If P0 exists:
Pack 110 must be P0 bugfix pack.

If no P0 but P1 exists:
Pack 110 must be P1 alpha blocker cleanup.

If no P0/P1 and users want more gameplay:
Pack 110 candidate can be one of:
- Daily Login claim live controlled rollout
- Achievements authoritative completion
- Soul Forge live controlled rollout
- Guild live runtime pack
- Story/Tower UX polish pack

Do not recommend live reward systems if any economy/reward invariant is uncertain.
