# 511 — Reward Claim UI Summary Preview Shell — Hardening v82

## File modificato
`frontend/app/reward-claim-summary-preview.tsx`

## Hardening v82
- Nuove **status chips**: "local staging apply", "live claim NOT active", "future live DB → dedicated pack"
- Nuova sezione **Status Snapshot (v82)** con counters separati:
  - `db_writes` (good)
  - `local_file_writes`
  - `observation_pass` (good)
  - `rollback_drill_executed`
  - `rolled_back_count`
  - `live_db_readiness_design_gate` (warn)
- Nuovi **labels chips**: `DB_WRITES_0`, `LOCAL_FILE_ONLY` (oltre a PREVIEW/STAGING/CANARY_LOCAL/NOT LIVE REWARD)
- Nuovi **emphasis styles**: `kvValueGood` (verde), `kvValueWarn` (arancio)
- `applied_to_live` evidenziato in WARN; `applied_to_local_staging` in GOOD
- Header subtitle aggiornato a `v82 hardened · wave-4`
- Banner aggiornato con distinzione live/staging
- Aggiunto sample `event_arena_ranking_reward` ai rejected examples
- Footer aggiornato con "Live DB richiede pack dedicato"

## Garanzie preservate (statiche)
- deeplink-only, no production UI exposure
- no backend fetch, no API call, no AsyncStorage, no account mutation, no DB
- no import battle_engine/story/combat
- **TypeScript pass** clean
- **Static checks PASS** (zero fetch reali, zero AsyncStorage, zero axios, zero `/api/`, zero process.env)

## Alpha Menu Patch
`alpha-menu-preview.tsx`: aggiornata entry `reward-claim-summary-preview` con label
"v82 hardened" e guardrails estesi (`local_file_writes_separate_counter`,
`live_db_readiness_design_only_no_apply`, labels `DB_WRITES_0|LOCAL_FILE_ONLY`).
