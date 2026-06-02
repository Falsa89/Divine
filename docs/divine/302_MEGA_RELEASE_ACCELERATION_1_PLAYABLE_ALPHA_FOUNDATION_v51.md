# 302 — MEGA RELEASE ACCELERATION 1 (v51)

**Pack**: `MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51`
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION`
**Strategic split**: 70% runtime/UI/test/asset integration · 30% safety/economy extra

## Tracks consegnate
- **Track A** — Material Raid Playable Alpha Slice (backend patch + 3 endpoint).
  Doc: `298_MATERIAL_RAID_PLAYABLE_ALPHA_SLICE.md`.
- **Track B** — Frontend Material Raid Alpha Screen (`material-raid-alpha.tsx`)
  deeplink-only, safe fallback se backend OFF.
- **Track C** — Visual Battle Routing Playable Slice Audit (design-only).
  Doc: `299_VISUAL_BATTLE_ROUTING_PLAYABLE_SLICE_AUDIT.md`.
- **Track D** — Asset Import Readiness ~40 Heroes (schema + report design-only).
  Doc: `300_ASSET_IMPORT_READINESS_40_HEROES.md`.
- **Track E** — Guide/Codex/Onboarding Alpha + `alpha-guide.tsx`.
  Doc: `301_GUIDE_CODEX_ONBOARDING_ALPHA_FOUNDATION.md`.
- **Track F** — Device QA and Beta Tester Smoke Matrix.
  Doc: `297_DEVICE_QA_AND_BETA_TESTER_SMOKE_MATRIX.md`.
- **Track G** — 6 validator + 6 marker + 6 tuple OPTIONAL nel suite runner.

## Tuple iniettate nel suite runner
1. `PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE`
2. `PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT`
3. `PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA`
4. `PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION`
5. `PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX`
6. `MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP`

## MD5 invarianti (5 file core)
- `backend/battle_engine.py` → `151ca35ad3bc35f0a6209cb3744ed440`
- `backend/.env` → `ff60bbb79efa329b71aa8ed351ea89b3`
- `backend/routes/artifacts.py` → `893f244d85fd45cbe825996463995293`
- `frontend/app/battlepass.tsx` → `54568b8cb75a07033f78ef6593aba839`
- `frontend/app/vip.tsx` → `45fcc9890b6b128c37088bc33aa54caf`

## Invarianti globali del pack
- `db_writes = 0`, `real_db_writes = 0`
- `production_db_touched = false`
- `mongo_url_used = false`, `pymongo_used = false`, `motor_used = false`, `redis_used = false`
- `filesystem_writes = 0`
- `live_apply_allowed = false`, `live_enforcement_enabled = false`
- `reward_claim_live = false`, `materials_granted = false`, `inventory_mutation = false`
- `server_py_changed = false`, `battle_engine_changed = false`,
  `combat_tsx_changed = false`, `story_tsx_changed = false`
- `existing_endpoint_paths_changed = false`, `existing_feature_flags_changed = false`,
  `existing_default_503_changed = false`, `safety_flags_changed = false`
- `validator_weakening = false`, `fake_pass = false`

## Verdetto atteso
`MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
