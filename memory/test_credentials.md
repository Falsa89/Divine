# Test Credentials (auto-managed, do not commit secrets)

## Pack 125 — QA Test Account

- **Email:** test@test.com
- **Username:** TestPlayer
- **User ID:** 651253e2-da8d-466b-98f3-82f008d158ed
- **QA team seed (Pack 124 + Pack 125):** applicato 10 eroi canonici (4 granted, 6 already_owned).

## Pack 125 — QA Team Save endpoint env vars

To enable QA team save server-scoped (`POST /api/team/save-formation`):

```bash
export QA_TEAM_SAVE_ENABLED=true
export QA_TEAM_SAVE_ALLOWLIST=651253e2-da8d-466b-98f3-82f008d158ed
# OR for any test account: QA_TEAM_SAVE_ALLOWLIST=*
```

Then restart backend: `sudo supervisorctl restart backend`.

Endpoint becomes available; otherwise returns 403 `QA_TEAM_SAVE_DISABLED`.

## Rollback QA seed

```bash
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_clear.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed
```
