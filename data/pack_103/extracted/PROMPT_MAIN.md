# MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_SUPERPACK

Execute after Pack 102.

Context:
- Pack 102 approved. Tower catalog v1 ready: 100 floors, deterministic 6v6 enemy teams.
- Boss floors are boss teams, not true boss monsters.
- All enemy hero IDs come from LAUNCH_BASE_HERO_IDS.
- Tower strict preview reads catalog_floor.
- Tower rewards remain OFF/quarantined.
- Tower execute is not live yet.
- Progress remains server-scoped through Pack 101 strict tower PSP path.
- Baseline expected around 1651/36/0.
- Note: previous public report/summary had commit hash mismatch; Pack 103 final report must use one consistent final commit hash.

Goal:
SUPERPACK 103 converts Tower from catalog/preview into a controlled playable loop:
1. Add strict Tower battle execute path.
2. Advance Tower progress server-scoped on PSP only.
3. Add ledger-backed reward source tower_floor_completion_claim.
4. Keep Tower reward live gated/OFF by default.
5. Connect safe Tower completion event to daily_quest_2.
6. Preserve S1/S2 isolation.
7. No premium/hard grant.
8. No reward_live_general.
9. No release readiness claim.

Approval:
Required exact authorization string:
AUTORIZZO_V110_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_PACK_103

Authorized only:
- Tower strict battle execute gated path.
- PSP.tower_progress server-scoped floor advancement.
- Reward source registry addition for tower_floor_completion_claim.
- Ledger/idempotency for tower floor claim.
- Daily quest event bridge hook: tower_floor_clear_success -> daily_quest_2.
- Test writes on Pack 103 marked users only.
- Smoke, validators, docs, frontend guard.

Not authorized:
- reward live activation generale
- premium/hard currency grant
- IAP/store/payment/gacha
- mail/achievements/battlepass/events/AFK rewards live
- broad production DB writes
- destructive migration
- legacy cleanup general
- account-wide tower progress
- release readiness claim

Required Design Rules:
Tower execute:
- endpoint example: POST /api/tower/strict/battle/execute?server_id=<sid>
- auth required, server_id required, PSP required
- idempotency_token required
- floor must equal current/next allowed floor for server profile
- uses catalog floor deterministic team
- no random, no battle_engine rewrite, no call to /api/battle/simulate
- no users.gold/gems/experience mutation
- no legacy tower route, no hardcoded s1

Tower progress:
- storage: PSP.tower_progress
- key scope: user_id + server_id + tower_id + floor + season
- S1 progress never affects S2
- advance only after valid victory
- replay same idempotency_token must not advance twice
- replay different token for same already-cleared floor must not advance twice

Tower reward:
- new source tower_floor_completion_claim
- ledger-backed and idempotent
- kill switch env default OFF, suggested: TOWER_FLOOR_CLAIM_ENABLED=false
- general ledger kill switch remains default OFF
- reward fixed server-side by floor band, no client payload
- allowed rewards only PSP soft currencies/materials if already server-scoped and safe
- no gems, no premium, no pull tickets, no hero/equipment direct grant in Pack 103

Daily quest 2 hook:
- event: tower_floor_clear_success
- maps to daily_quest_2 only if tower execution is server-authoritative and server-scoped
- no client free proof, no reward grant in event bridge
- claim daily_quest_2 still goes through daily_quest_completion_claim ledger
- S1 tower clear completes daily_quest_2 on S1 only, not S2

Required Tracks:
A Baseline 3-run suite.
B Tower execute SOT.
C Tower execution endpoint.
D PSP progress advancement and idempotency.
E Tower floor completion claim registry source.
F Tower reward ledger claim endpoint/path.
G Daily quest 2 tower clear hook.
H Frontend Tower execute/claim guard.
I Kill switches and flags.
J Runtime Smoke E2E.
K Static tower execute/reward anti-leak guard.
L Legacy/non-regression audit.
M Data invariants / forbidden mutation proof.
N Cleanup/rollback.
O Live readiness update.
P MD5 rebase if needed, no validator weakening.
Q Gate/runtime invariant preservation.
R Final 3-run suite.
S Rollup validator and runner integration.

Smoke E2E required proof:
1. unmarked users refused
2. kill switches OFF by default
3. S1 and S2 PSP created/isolated
4. execute/clear floor 1 on S1 with idempotency token succeeds only if gated smoke flags ON
5. S1 tower progress advances and S2 unchanged
6. replay same token no second progress/reward
7. replay different token for already-cleared floor no double reward/advance
8. claim tower_floor_completion_claim only once
9. users.gold/gems/experience unchanged
10. tower_floor_clear_success completes daily_quest_2 on S1 only
11. daily_quest_2 on S2 remains incomplete
12. invalid floor/catalog out of range blocked
13. legacy tower endpoints remain quarantined
14. frontend default flags OFF/no leak
15. Packs 91-102 preserved
16. cleanup verified

Forbidden Scope:
NO reward live activation generale
NO tower reward live without specific kill switches and ledger idempotency
NO premium/hard currency grant
NO users.gold/gems/experience mutation from tower
NO broad production DB writes
NO legacy cleanup general execute
NO destructive migration
NO account-wide tower progress write
NO hardcoded server_id=s1
NO S1 progress leak into S2
NO invalid/legacy/hidden hero IDs in tower path
NO random enemy teams
NO true boss monsters
NO gacha/IAP/payment change
NO mail/achievement/battlepass/event/AFK rewards live
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

Expected Verdicts:
READY: MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
GATED: MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_READY_REWARD_CLAIM_READY_GATED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
UNSAFE: MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_CONDITIONAL_BLOCKERS_REWARD_OR_SERVER_SCOPE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Final Report:
docs/divine/110_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_FINAL_REPORT.md
Must include verdict, final commit hash, diff stat, baseline/final suite, tower execute endpoint, PSP progress advancement, tower_floor_completion_claim, ledger/idempotency, daily_quest_2 hook, frontend guard, kill switches, smoke E2E, static anti-leak guard, data invariants, cleanup/rollback, live readiness update, MD5/gate preservation, S1/S2 isolation, no users.gold/gems/experience mutation, no premium/hard grants, reward_live_general=false, tower reward live status, daily_quest_2 status, Pack 91-102 preservation, deferred blockers and next step.
