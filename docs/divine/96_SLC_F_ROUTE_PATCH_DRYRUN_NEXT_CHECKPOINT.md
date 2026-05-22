# Next Checkpoint — SLC-F Route Patch Dry-Run

SLC-F remains the next recommended checkpoint after this canonical benchmark source pack.

Mode: DESIGN-ONLY / AUDIT-ONLY / READ-ONLY / DRY-RUN.

Purpose:
- Identify every route/collection/system that must become server-aware.
- Create patch contracts and dry-run simulation only.
- Do not apply runtime route changes.

Baseline:
- SLC-C complete.
- SLC-BE complete.
- LIVE-MODES-RECONCILIATION-A complete.
- Suite previous baseline: 278 PASS / 0 FAIL / 0 MISS.
- SECOND_SERVER_OPENING_ENABLED unset.
- SERVER_PROFILES_RUNTIME_ENABLED unset.
- second_server_opening_allowed=false.

SLC-F required outputs:
- server-aware route patch matrix;
- per-route risk classification;
- server-bound/account-wide collection mapping;
- pseudo-diff / patch contract only;
- dry-run resolver simulation for account_id + server_id;
- protected-file no-diff audit;
- DB no-write audit;
- future phase recommendations.

Hard guardrails:
- No runtime patch.
- No DB writes.
- No migrations.
- No route creation.
- No auth runtime change.
- No UI.
- No second server opening.
- No changes to battle_engine.py, battle_core.py, combat.tsx.
- No changes to affinity_gift_spend.py or AF2-N/Stage4.

Acceptance:
- route_patch_applied=false;
- db_write=false;
- migration_applied=false;
- second_server_opening_allowed=false;
- future_feature_flags remain false/unset;
- SLC-F docs and validators PASS;
- suite PASS;
- API smoke PASS.
