# 268 — Material Raid Canary QA Rehearsal Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_8_..._v44` · Track C  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY · **DB writes**: `0`

## Scopo

Rehearsal **design-only** del pilot canary `material_raid_claim` con 7 scenari
definiti, **senza** flip di signoff/canary/live:

- `signoff_state=pending`, `canary_enabled=false`, `canary_percentage=0`
- `live_enabled=false`, `reward_grant_enabled=false`, `material_grant_enabled=false`

## Scenari (7)

1. **SCN_HAPPY_PATH** — happy path single claim preview
2. **SCN_DUPLICATE_SAME_HASH** — stesso CK + stesso payload (replay)
3. **SCN_DUPLICATE_DIFF_HASH** — stesso CK + payload diverso (conflict via client-key v44)
4. **SCN_VERSION_MISMATCH** — contract version mismatch (validation fails, no live escalation)
5. **SCN_UNAUTHORIZED** — nessun auth header (route preview unauthenticated by design)
6. **SCN_FLAG_DISABLED** — feature flag OFF → HTTP 503, buffer non cresce
7. **SCN_ROLLBACK_TRIGGER** — trigger ALERT_DB_WRITES_NONZERO → rollback template dry-run (idempotente)

## Approver richiesti per signoff approved

`game_director`, `technical_producer`, `qa_owner`, `rollback_owner`.

## Kill switch

`MATERIAL_RAID_CLAIM_CANARY_KILL_SWITCH` default `engaged_kill`.
