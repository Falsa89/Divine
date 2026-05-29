# 181G — VIP Future Implementation Roadmap

**Track:** G — Future Implementation Roadmap
**Verdict:** `TRACK_G_VIP_FUTURE_IMPLEMENTATION_ROADMAP_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## 9 Stage espliciti

### Stage 1 — `VIP_DESIGN_AND_IAP_INTEGRATION_SIGNOFF_LOCKED`
- **Descrizione:** Questo pack. Canonical VIP design + IAP entitlement mapping, locked.
- **Required signoff markers:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_APPROVAL=true`
- **Blockers prima di avanzare:** public repo sync verification di questo pack
- **Rollback:** revert commit; no DB/runtime affected

### Stage 2 — `VIP_TIER_THRESHOLD_SIGNOFF`
- **Descrizione:** Fill `<<VIP_TIER_X>>` placeholders con final spend thresholds; explicit benefit table per tier.
- **Required signoff markers:** `PROJECT_VIP_TIER_THRESHOLD_APPROVAL`
- **Blockers:** economy team review, anti-P2W recheck
- **Rollback:** revert threshold JSON

### Stage 3 — `VIP_SCHEMA_DRY_RUN`
- **Descrizione:** Mongo schema dry-run per `vip_points_ledger` + `vip_status_snapshot`. Indexes, idempotency. No live writes.
- **Required signoff markers:** `PROJECT_VIP_SCHEMA_DRY_RUN_APPROVAL`
- **Blockers:** unique index plan, idempotency plan
- **Rollback:** drop indexes (no data ever written)

### Stage 4 — `VIP_BACKEND_ENDPOINTS_DEV_ONLY`
- **Descrizione:** Implementare `/api/vip/status`, `/claim-daily`, `/grant`, `/revoke`, `/history` dietro feature flags `VIP_*_ENABLED=false`.
- **Required signoff markers:** `PROJECT_VIP_BACKEND_DEV_APPROVAL`
- **Blockers:** feature flags forced off in production
- **Rollback:** unmount routes

### Stage 5 — `VIP_LOCKED_UI_MODERNIZATION_IMPLEMENTATION`
- **Descrizione:** Implementare Track E copy + tier ladder preview in `frontend/app/vip.tsx`; mantenere `VIP_LOCKED_V2 = true`; no claim, no buy.
- **Required signoff markers:** `PROJECT_VIP_LOCKED_UI_IMPL_APPROVAL`
- **Blockers:** copy review, accessibility review
- **Rollback:** revert `vip.tsx`

### Stage 6 — `VIP_CANARY_PROGRESSION`
- **Descrizione:** Abilitare grant `vip_points` + tier compute solo per canary internal users (`sfqa@test.com`, `test@test.com`).
- **Required signoff markers:** `PROJECT_VIP_PROGRESSION_CANARY_APPROVAL=true`
- **Canary users expected:** `sfqa@test.com`, `test@test.com`
- **Blockers:** 178F Stage 6 canary fulfillment green, 179 Track D wallet ledger ready
- **Rollback:** disable allowlist; archive ledger

### Stage 7 — `VIP_DAILY_CLAIM_CANARY`
- **Descrizione:** Abilitare `/api/vip/claim-daily` solo per canary users; verify idempotency + correct crystal stipend.
- **Required signoff markers:** `PROJECT_VIP_DAILY_CLAIM_CANARY_APPROVAL=true`
- **Blockers:** Stage 6 progression canary green
- **Rollback:** disable allowlist; revoke via ledger

### Stage 8 — `VIP_REFUND_REVOKE_TEST`
- **Descrizione:** Eseguire Apple ASSN / Google RTDN refund webhooks su canary VIP points; verify tier demotion correctness.
- **Required signoff markers:** `PROJECT_VIP_REFUND_TEST_APPROVAL`
- **Blockers:** 179 refund-reconcile design + Stage 7 of 178F roadmap
- **Rollback:** document and re-run

### Stage 9 — `VIP_PUBLIC_RELEASE_GATE`
- **Descrizione:** Flip `VIP_LOCKED_V2 = false` in production; enable claim + benefits.
- **Required signoff markers:** `PROJECT_VIP_RELEASE_GATE_APPROVAL`
- **Blockers:** Stages 1-8 verified, 178F Release Gate alignment, 179 Stage 8 Public Shop IAP UI live
- **Rollback:** emergency `VIP_LOCKED_V2=true`; pause writes; freeze tiers

## Alignment con altre roadmap
- `vip_canary_stage_6_blocks_on_178F_stage_6`: `true`
- `vip_canary_stage_6_blocks_on_179_track_D`: `true`
- `vip_refund_test_stage_8_blocks_on_178F_stage_7`: `true`
- `vip_release_gate_stage_9_blocks_on_178F_release_gate_stage_10`: `true`
- `vip_release_gate_stage_9_blocks_on_179_stage_8`: `true`

## Verdict
`TRACK_G_VIP_FUTURE_IMPLEMENTATION_ROADMAP_READY` — 9 stage monotonici (1..9), canary scope sfqa+test, blockers cross-roadmap espliciti, rollback per ogni stage.
