# 152D — Track D: Server Profile Migration Risk Matrix

**Verdict:** `TRACK_D_SERVER_PROFILE_MIGRATION_RISK_MATRIX_READY` · audit-only

## State pre-audit
- `users.server` (string) usato come unica fonte verità attuale.
- `server_profiles` collection: 0 doc (assunto).
- Map `users.server ↔ server_profile_id`: **NON ESISTE**.

## Risk matrix (7 voci)
| Risk | Severity | Likelihood today | Mitigation |
|---|---|---|---|
| Orphan users (flag ON senza seed) | **CRITICAL** | only if premature flip | NO flag flip until seed pack |
| Diverging state | HIGH | prevented | dual-write before cutover |
| Concurrent legacy writes | HIGH | low | lock /servers UI |
| Capacity check bypass | MEDIUM | n/a | reimplement checks |
| Rollback complexity | MEDIUM | n/a | runbook con inverso |
| Auth scope drift | HIGH | prevented (503) | aggiungere auth |
| 503 unhandled client | LOW | n/a | wrapper feature_disabled |

## Strategia dual-write (6 fasi)
0. safe-now: no writes (current).
1. seed: backfill server_profiles da users.server.
2. dual_write: nuovo POST scrive entrambi.
3. read_through: nuovo GET legge profile_id + fallback.
4. cutover: frontend al nuovo endpoint.
5. deprecate: HTTP Sunset header.

**Lock durante transizione: REQUIRED.**

## Risk: HIGH
