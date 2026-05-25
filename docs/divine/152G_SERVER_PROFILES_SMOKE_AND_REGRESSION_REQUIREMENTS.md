# 152G — Track G: Smoke & Regression Requirements

**Verdict:** `TRACK_G_SERVER_PROFILES_SMOKE_AND_REGRESSION_REQUIREMENTS_READY` · audit-only

## Smoke categories (7)
1. **Legacy endpoint smoke** — `GET /api/servers` 200, `POST /api/server/select` 401 no-auth, 404 bad id, 400 maint, **NO write durante audit**.
2. **New endpoint smoke** — `GET/POST /api/server-profiles/select` 503 con `status:'disabled'`.
3. **UI smoke** — `/servers` renderizza, menu visibile, no auto-tap.
4. **Flag state smoke** — RUNTIME e PREVIEW flag NOT set.
5. **DB state smoke** — `server_profiles` count==0, `users.server` invariato.
6. **Rollback validation** — MD5 invariants.
7. **Mobile QA** — render su 390x844 e 360x800.

## Forbidden smoke actions (5)
- no POST `/api/server/select` con payload validi
- no flag flip
- no DB write
- no concurrent migration test
- no fake mobile QA screenshot

## Future regression validators (4)
- `validate_server_profiles_select_503_when_flag_off.py`
- `validate_legacy_server_select_deprecation_log_present.py`
- `validate_server_profiles_db_count_baseline.py`
- `validate_servers_ui_locks_or_calls_new_endpoint_after_cutover.py`
