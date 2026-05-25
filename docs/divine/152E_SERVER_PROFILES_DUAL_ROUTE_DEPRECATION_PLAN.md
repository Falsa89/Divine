# 152E — Track E: Dual-Route Deprecation Plan

**Verdict:** `TRACK_E_SERVER_PROFILES_DUAL_ROUTE_DEPRECATION_PLAN_READY` · audit-only

## 8 stages (paper-only)
| # | Stage | DB writes | Flag flips | Status |
|---|---|---|---|---|
| 1 | AUDIT_ONLY (current) | 0 | 0 | IN_PROGRESS |
| 2 | LOCK_OR_PREVIEW_UI | 0 | 0 | PENDING |
| 3 | READ_ONLY_PREVIEW_SAFE | 0 | 0 | PENDING |
| 4 | DUAL_ROUTE_COMPATIBILITY_LAYER | flag only | add flag | PENDING |
| 5 | SEED_AND_BACKFILL | YES seed | 0 | PENDING |
| 6 | UI_CUTOVER_BEHIND_FLAG | via dual-write | RUNTIME+CUTOVER | PENDING |
| 7 | DEPRECATE_LEGACY_HEADERS | 0 | 0 | PENDING |
| 8 | REMOVE_LEGACY_AFTER_GRACE | model migration | retire flags | PENDING |

## Esistente vs proposto
`/app/docs/divine/120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md` definisce un piano 4-fasi.
Questo pack lo espande a 8 stage aggiungendo LOCK_OR_PREVIEW e READ_ONLY_PREVIEW_SAFE tra audit e dual-write.
