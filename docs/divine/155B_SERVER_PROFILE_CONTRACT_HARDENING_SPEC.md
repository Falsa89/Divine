# 155B — Server Profile Contract Hardening Spec

**Verdict:** `TRACK_B_SERVER_PROFILE_CONTRACT_HARDENING_SPEC_READY` · design-only

## 3 endpoint nel draft
| Endpoint | Auth | Flag gating | Mutation |
|---|---|---|---|
| GET `/api/account/server-profiles/preview` | get_current_user | RUNTIME + PREVIEW | ❌ |
| GET `/api/account/server-profiles` | get_current_user | RUNTIME | ❌ |
| POST `/api/account/server-profiles/select` | get_current_user | RUNTIME (+ DUAL_WRITE opzionale) | ✅ dopo validation |

## Error envelopes coerenti
- 401 unauthorized
- 400 capacity · 400 maintenance · 400 archived
- 404 not_found
- 500 internal + `rollback_executed:true`

## Validazione su POST `/select`
1. ownership check
2. server reachable (404)
3. server NOT maintenance (400)
4. server NOT full (400)
5. profile NOT archived (400)

## Non-mutation invariants preview
- idempotent · no writes · no `users.server` change · no `active_server_profile_id` change
