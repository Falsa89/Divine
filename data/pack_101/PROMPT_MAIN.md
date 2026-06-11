# MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE

Execute after Pack 100.

Context:
- Pack 100 approved. Daily task loop ready for daily_quest_1.
- Story strict server-scope OK.
- Tower is still deferred because legacy tower progress/reward path can be account-wide and may mutate users.gold/users.gems/users.experience.
- Canonical rule: gameplay progression is user_id + server_id + feature_scope. S1 tower progress must never appear on S2.

Approval string required:
AUTORIZZO_V110_TOWER_PROGRESS_PSP_MIGRATION_REWARD_QUARANTINE_PACK_101

Authorization scope only:
- Tower server-scoped schema/loader/status/progress preview.
- Tower reward quarantine.
- Test-only writes marked Pack 101.
- Smoke E2E for S1/S2 isolation.
- Validators/docs/report.

Not authorized:
- tower reward live grant
- premium/hard grants
- broad production DB writes
- destructive migration
- account-wide tower progress write
- legacy cleanup general
- release readiness claim

Goals:
1. Define Tower server-scope SOT.
2. Audit all tower legacy paths.
3. Implement or prepare PSP/server-scoped tower progress loader.
4. Add strict GET /api/tower/status?server_id=<sid>.
5. Add strict preview/battle/progress path with NO reward live.
6. Quarantine tower rewards behind ledger-required/deferred blockers.
7. Ensure frontend tower consumers pass server_id or show locked/deferred.
8. Prove S1/S2 tower isolation in smoke.
9. Preserve Packs 84-100.
10. Keep reward_live_general=false.

Required tracks:
A baseline 3-run suite.
B Tower server-scope SOT.
C Tower legacy path audit.
D PSP tower progress schema/loader.
E Tower backfill preflight only unless separate apply authorization is given.
F Tower status strict endpoint.
G Tower battle/progress strict preview.
H Tower reward quarantine.
I Frontend tower consumer guard.
J Story/Daily/Tower server-scope cross validator.
K Runtime smoke E2E.
L Static tower anti-leak guard.
M Data invariants.
N Cleanup/rollback.
O Live readiness update.
P MD5 rebase only if needed, with no validator weakening.
Q Gate/runtime invariant preservation.
R Final 3-run suite.
S Rollup validator and runner integration.

Forbidden:
NO tower reward live grant
NO reward live activation generale
NO premium/hard currency grant
NO users.gold/gems/experience mutation from tower
NO broad production DB writes non-gated
NO legacy cleanup general execute
NO destructive migration
NO account-wide tower progress write
NO hardcoded server_id="s1" in active tower path
NO S1 progress leak into S2
NO gacha/IAP/payment change
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

Expected ready verdict:
MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If only preflight/not applied:
MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_READY_NOT_APPLIED_PENDING_BACKFILL_APPROVAL_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If leak remains:
MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_CONDITIONAL_BLOCKERS_SERVER_SCOPE_OR_REWARD_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Final report:
docs/divine/110_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE_FINAL_REPORT.md

Final report must explicitly state:
- tower progress server-scope status
- tower reward live status
- S1/S2 tower isolation
- no users.gold/gems/experience mutation from tower
- reward_live_general remains false
- no premium/hard grants
- Pack 91/93/94/95/96/97/98/99/100 preserved
- deferred blockers and next step
