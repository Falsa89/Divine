# v108_AUTHORITATIVE — Rollback Plan

**Sentinel:** `PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER`

Questo pack NON esegue rollback e NON scrive DB. Definisce il piano.

## Backup obbligatori
users, user_heroes, team_formation, battle_pass_progress, vip_progress, user_equipment, hero_progression_log, battle_resolution_ledger (futuro).

## Kill flags
- `REWARD_LIVE_ENABLED → false`
- `PROGRESS_LIVE_ENABLED → false`
- `BATTLE_LAUNCH_AUTHORITATIVE_ENABLED → false`
- `SERVER_SCOPED_RUNTIME_ENABLED → false`

## Ledger replay
Ledger entries con `created_at > T_rollback` marcate `rolled_back`. Per ogni `status=applied`, reverse delta su user_heroes/user_equipment/battle_pass_progress/vip_progress.

## Abort conditions
Loader filter_applied=false / PSP non applicato / legacy cleanup non applicato / POSTQA_D gates unlocked / runtime invariant regression / required_fail>0.

## Snapshot plan
`mongodump --archive=auth_live_pre_flip_snapshot.gz` prima del flip. Verify count match post-flip. Abort se delta inatteso.

## Smoke plan
happy 6-slot 200, flag_off 423 su tutti i live codes, ledger replay duplicate → `conflict_duplicate`, snapshot DB invariato.
