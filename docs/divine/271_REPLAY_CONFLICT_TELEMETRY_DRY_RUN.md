# 271 — REPLAY_CONFLICT_TELEMETRY_DRY_RUN (v45 Track B)

## Sintesi
Wire-up del contratto telemetry dry-run sulle 8 safety preview route. Le route
emettono un envelope `replay_conflict_telemetry_dry_run` nelle POST response,
espongono `observability_aggregation_dry_run` in `/config` e `aggregation_snapshot`
in `/peek-buffer`.

## Routes coperte (8/8)
- gem_socket_commit_safety_preview
- material_raid_claim_safety_preview
- gear_forge_fusion_safety_preview
- rune_scroll_talisman_safety_preview
- artifact_upgrade_safety_preview
- divine_weapon_upgrade_safety_preview
- battle_pass_claim_safety_preview
- mail_claim_safety_preview

## Counters
- v43 server-key: `new_key_preview`, `same_key_same_hash_replay_preview`, `same_key_diff_hash_conflict_preview`, `missing_key_preview`
- v44 client-key: `new_client_key_preview`, `same_client_key_same_hash_replay_preview`, `same_client_key_diff_hash_conflict_preview`, `missing_client_key_preview`

## Invarianti rispettati
- NESSUN cambio endpoint path / feature flag / default 503 / safety flag.
- NESSUN cambio a `backend/server.py`.
- NESSUN cambio frontend.
- 0 DB writes, 0 Redis, 0 filesystem persistence, 0 persistent ledger.
- Preview request MAI bloccata dalla telemetry.
