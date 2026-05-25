# 151F — Track F: Mode Smoke Test Requirements

**Verdict:** `TRACK_F_MODE_SMOKE_TEST_REQUIREMENTS_READY`
**Mode:** audit-only (no destructive smoke)

## Summary
- 27 modalità con smoke specifica
- P1: 7 (`heroes`, `combat`, `daily_hub`, `artifact`, `housing`, `status_runtime_*`, `server_profiles`)
- P2: 14
- P3: 6
- Locked-state guards: 6
- Regression validators raccomandati: 11

## P1 smoke must-haves
1. **heroes**: `GET /api/heroes` len==100 • `borea==200` • `primordial_gaia==404`.
2. **combat**: `md5 battle_engine.py == 151ca35ad3bc35f0a6209cb3744ed440` • battle plays.
3. **daily_hub**: render • 0 claim buttons • 5 link target existing routes.
4. **artifact**: `/artifacts-preview` shows locked card • 0 mutation buttons.
5. **housing**: `GET /api/housing/preview == 503` • locked card.
6. **status_runtime_first_slice**: flag NOT set.
7. **status_runtime_second_slice**: flag NOT set in prod env.
8. **server_profiles**: `/api/server-profiles/select == 503` • audit `/servers` UI usage.

## Forbidden smoke actions
no destructive smoke • no live gacha pulls • no economy mutations • no DB writes • no fake mobile screenshots.

## Audit constraints respected
This pack defines requirements only — no smoke was executed beyond passive API health probes.
