# 303 — Material Raid Visual Battle Payload Contract v2

**Pack**: `MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK_v52`
**Track**: A
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA`
**Contract**: `material_raid_visual_battle_payload_contract_v2`

## Scopo
Definire il contratto deterministico tra il backend `/api/material-raid/alpha-battle-preview` e
la schermata frontend `/material-raid-visual-preview`.

## Endpoint / route
- **Source endpoint**: `POST /api/material-raid/alpha-battle-preview`
- **Target frontend route**: `/material-raid-visual-preview`
- **Mode**: `material_raid`

## Required payload fields
`mode`, `track_id`, `stage_id`, `recommended_power`, `team_power`,
`enemy_family_preview`, `battle_seed_preview`, `battle_visual_required`,
`auto_resolve_allowed`, `result_authoritative`, `reward_claim_enabled`,
`materials_granted`, `db_writes`.

## Garanzie hard
- `visual_battle_required = true`
- `auto_resolve_allowed = false` (Guild War è l'unica eccezione globale, qui non si applica)
- `battle_engine_runtime_used = false`
- `battle_engine_py_changed = false`
- `result_authoritative = false`
- `reward_grant_enabled = false`
- `materials_granted = false`
- `reward_claim_enabled = false`
- `db_writes = 0`
- `alpha_preview_only = true`

## Aggiunte append-only nel payload backend
- `result_authoritative`, `alpha_preview_only`, `battle_engine_runtime_used`,
  `reward_grant_enabled`, `target_frontend_route`,
  `background_hint`, `music_hint`, `tutorial_hint`, `reward_preview_hint`.

Nessun cambio a path, flag, default 503, status, comportamento locked/underpowered.
