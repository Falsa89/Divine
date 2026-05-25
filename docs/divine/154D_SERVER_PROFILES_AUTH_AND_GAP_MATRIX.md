# 154D — Server Profiles Auth & Gap Matrix

**Verdict:** `TRACK_D_SERVER_PROFILES_AUTH_AND_GAP_MATRIX_READY` · audit-only

## Gap matrix (8 voci)
| Gap | Severity | Stato | Required before | Owner pack |
|---|---|---|---|---|
| Auth missing su nuovo POST | HIGH | endpoint 503; no auth wired | flag flip | AUTH_AND_CONTRACT_HARDENING |
| Capacity check missing | MEDIUM | inert | flag flip | AUTH_AND_CONTRACT_HARDENING |
| Maintenance check missing | MEDIUM | inert | flag flip | AUTH_AND_CONTRACT_HARDENING |
| **Seed/backfill missing** | **CRITICAL** | server_profiles=0 doc | flag flip / migration | SEED_AND_ROLLBACK_PLAN |
| Dual-write strategy missing | HIGH | solo legacy scrive | UI cutover | DUAL_WRITE_DESIGN |
| **Orphan-user risk** | **CRITICAL** | prevenuto da 503 gating | flag flip | SEED_AND_ROLLBACK_PLAN |
| UI 503 handling | LOW | già gestito via SafeFeatureCard | — | già risolto (153) |
| Rollback documentato ma non rehearsed | MEDIUM | piano in 152E | seed pack | SEED_AND_ROLLBACK_PLAN |

## Distribuzione severità
- CRITICAL: 2
- HIGH: 2
- MEDIUM: 3
- LOW: 1

## Flag flip authorized
**NO** — 6 blockers tra CRITICAL/HIGH/MEDIUM. Auth + seed devono atterrare prima.
